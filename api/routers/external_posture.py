from .jst import JST
from datetime import datetime
from fastapi import APIRouter
from models.external_posture import external_posture as external_posture_model
from config.db import conn
from schemas.external_posture import ExternalPosture, ExternalPosturePost, ExternalPosturePut
from sqlalchemy import select, desc
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

@external_posture.post("/")
async def post_external_posture(external_posture: ExternalPosturePost) -> ExternalPosture:
    conn.execute(external_posture_model.insert().values(
        **external_posture.dict(),
        created_at = datetime.now(JST)
    ))
    conn.commit()
    return conn.execute(select(external_posture_model).order_by(desc(external_posture_model.c.created_at))).first()

@external_posture.put("/{id}")
async def update_internal_posture_id(id: int, external_posture: ExternalPosturePut) -> ExternalPosture:
    conn.execute(external_posture_model.update().values(
        **external_posture
    ).where(external_posture_model.c.id==id))
    conn.commit()
    return conn.execute(select(external_posture_model).where(external_posture_model.c.id==id)).first()