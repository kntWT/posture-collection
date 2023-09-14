from .jst import JST
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.user import user as user_model
from config.db import conn
from schemas.user import User, UserPost, UserCalibrateInternalPosture, UserCalibrateExternalPosture
from sqlalchemy import select, desc
from typing import List

user = APIRouter(prefix="/user")
security = HTTPBasic()

@user.post("/")
async def create_user(user: UserPost) -> User:
    conn.execute(user_model.insert().values(
        **user.dict(),
        created_at = datetime.now(JST)
    ))
    conn.commit()
    return conn.execute(select(user_model).order_by(desc(user_model.c.created_at))).first()

@user.get("/auth/")
async def auth_basic(credentials: HTTPBasicCredentials = Depends(security)):
    username: str = credentials.username
    password: str = credentials.password
    tmp_user: User = conn.execute(select(user_model).filter(user_model.c.name==username and user_model.c.password==password)).first()
    if tmp_user is None:
        raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basci"}
            )
    else:
        return tmp_user._asdict()
    

@user.get("/")
async def get_users() -> List[User]:
    return conn.execute(select(user_model)).fetchall()

@user.get("/{id}")
async def get_user_by_id(id: int) -> User:
    return conn.execute(select(user_model).filter(user_model.c.id==id)).first()

@user.get("/guest/")
async def get_guest_user() -> User:
    return conn.execute(select(user_model).filter(user_model.c.id==1)).first()

@user.put("/calibration/internal-posture/{id}")
async def update_user_calibration(id: int, user: UserCalibrateInternalPosture) -> User:
    conn.execute(user_model.update().values(
        neck_to_nose_standard = user.neck_to_nose_standard
    ).where(user_model.c.id==id))
    conn.commit()
    return  conn.execute(select(user_model).filter(user_model.c.id==id)).first()

@user.put("/calibration/external-posture/{id}")
async def update_user_calibration(id: int, user: UserCalibrateExternalPosture) -> User:
    conn.execute(user_model.update().values(
        neck_angle_offset = user.neck_angle_offset
    ).where(user_model.c.id==id))
    conn.commit()
    return  conn.execute(select(user_model).filter(user_model.c.id==id)).first()