from .jst import JST
from datetime import datetime
from fastapi import APIRouter
from models.internal_posture import internal_posture as internal_posture_model
from config.db import conn
from schemas.internal_posture import InternalPosture, InternalPostureOnlyOrientation, InternalPostureOnlyEstimation
from sqlalchemy import select, desc
from typing import List

internal_posture = APIRouter(prefix="/internal-posture")

@internal_posture.get("/")
async def get_internal_postures() -> List[InternalPosture]:
    return conn.execute(select(internal_posture_model)).fetchall()

@internal_posture.get("/{user_id}")
async def get_internal_posutres_by_user_id(user_id: int) -> List[InternalPosture]:
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.user_id==user_id)).fetchall()

@internal_posture.get("/{id}")
async def get_internal_posture_by_id(id: int) -> InternalPosture:
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.id==id)).first()

@internal_posture.post("/")
async def post_internal_posture_only_orientation(internal_posture_only_orientation: InternalPostureOnlyOrientation) -> InternalPosture:
    conn.execute(internal_posture_model.insert().values(
        **internal_posture_only_orientation,
        created_at = datetime.now(JST)
    ))
    return conn.execute(select(internal_posture_model).order_by(desc(internal_posture_model.c.created_at))).first()

@internal_posture.put("/{id}")
async def update_estimation(internal_posture_only_estimation: InternalPostureOnlyEstimation) -> InternalPosture:
    conn.execute(internal_posture_model.update().values(
        **internal_posture_only_estimation
    ).where(internal_posture_model.c.id==id))
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.id==id)).first()