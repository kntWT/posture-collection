from .jst import JST
from datetime import datetime
from fastapi import APIRouter
from models.user import users as user_model
from config.db import conn
from schemas.user import User, UserPost, UserPut
from sqlalchemy import select
from typing import List

user = APIRouter(prefix="/user")

@user.post("/")
async def create_user(user: UserPost) -> User:
    conn.execute(user_model.insert().values(
        **user,
        created_at = datetime.now(JST)
    ))
    return conn.execute(select(user_model).filter(user_model.c.id==user.id)).first()

@user.get("/")
async def get_users() -> List[User]:
    return conn.execute(select(user_model))

@user.get("/{id}")
async def get_user_by_id(id: int) -> User:
    return conn.execute(select(user_model).filter(user_model.c.id==id)).first()

@user.put("/calibration/{id}")
async def update_user_calibration(id: int, user: UserPut) -> User:
    conn.execute(user_model.update().values(
        neck_to_nose_standard = user.neck_to_nose_standard
    ).where(user_model.c.id==id))
    return  conn.execute(select(user_model).filter(user_model.c.id==id)).first()