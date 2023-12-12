from fastapi import APIRouter
from models.external_posture import external_posture as external_posture_model
from models.user import user as user_model
from config.db import conn
from helpers import to_csv
from schemas.external_posture import ExternalPosture, ExternalPosturePost, ExternalPostureWithUser
from sqlalchemy import select, asc, desc
from typing import List

external_posture = APIRouter(prefix="/external-posture")

@external_posture.get("/")
async def get_external_postures() -> List[ExternalPosture]:
    return conn.execute(select(external_posture_model)).fetchall()

@external_posture.get("/{user_id}")
async def get_external_posutres_by_user_id(user_id: int) -> List[ExternalPosture]:
    return conn.execute(select(external_posture_model).where(external_posture_model.c.user_id==user_id)).fetchall()

@external_posture.get("/{id}")
async def get_external_posture_by_id(id: int) -> ExternalPosture:
    return conn.execute(select(external_posture_model).where(external_posture_model.c.id==id)).first()

@external_posture.get("/{user_id}/joined/")
async def get_external_posture_by_user_id_joined(user_id: int) -> List[ExternalPostureWithUser]:
    return conn.execute(select(external_posture_model, user_model).
                        where(external_posture_model.c.user_id==user_id).
                        join(user_model, user_model.c.id==external_posture_model.c.user_id).
                        order_by(asc(external_posture_model.c.id))
            ).fetchall()

@external_posture.post("/")
async def post_external_posture(external_posture: ExternalPosturePost) -> ExternalPosture:
    conn.execute(external_posture_model.insert().values(
        **external_posture.dict(),
    ))
    conn.commit()
    return conn.execute(select(external_posture_model).filter(external_posture_model.c.created_at==external_posture.created_at)).first()

@external_posture.post("/list/")
async def post_external_posture_list(external_postures: List[ExternalPosturePost]) -> List[ExternalPosture]:
    if len(external_postures) == 0:
        return []
    dict_list = [external_posture.dict() for external_posture in external_postures]
    conn.execute(external_posture_model.insert().values(
        dict_list
    ))
    conn.commit()
    first_data = external_postures[0]
    user_id = first_data.user_id
    created_at = first_data.created_at.strftime("%Y-%m-%d_%H:%M:%S.%f")
    to_csv(dict_list, f"data/input/external_posture/{user_id}/{created_at}.csv")
    return conn.execute(select(external_posture_model).filter(external_posture_model.c.created_at in [e.created_at for e in external_postures])).fetchall()