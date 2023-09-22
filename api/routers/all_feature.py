from fastapi import APIRouter
from models.user import user as user_model
from models.internal_posture import internal_posture as internal_posture_model
from models.external_posture import external_posture as external_posture_model
from sqlalchemy import select, func, text, and_
from typing import List

from config.db import conn

all_feature = APIRouter(prefix="/all-feature")

@all_feature.get("/")
async def get_all_features() -> List:
    statement = select(
        internal_posture_model,
        external_posture_model,
        user_model
    ).join(
        external_posture_model,
        and_(
            and_(
                func.timestampdiff(text("MICROSECOND"), internal_posture_model.c.created_at, external_posture_model.c.created_at) > -25000,
                func.timestampdiff(text("MICROSECOND"), internal_posture_model.c.created_at, external_posture_model.c.created_at) < 25000
            ),
            internal_posture_model.c.user_id == external_posture_model.c.user_id
        )
    ).join(
        user_model,
        internal_posture_model.c.user_id == user_model.c.id
    )
    responces = conn.execute(statement).fetchall()
    result = []
    for res in responces:
        data = res._asdict()
        data["internal_posture_id"] = data.pop("id")
        data["internal_posture_created_at"] = data.pop("created_at")
        data["external_posture_id"] = data.pop("id_1")
        data["external_posture_created_at"] = data.pop("created_at_1")
        data["user_id"] = data.pop("id_2")
        data["user_created_at"] = data.pop("created_at_2")
        result.append(data)

    return result

@all_feature.get("/{microseconds}")
async def get_al_features_with_param(microseconds: int):
    statement = select(
        internal_posture_model,
        external_posture_model,
        user_model
    ).join(
        external_posture_model,
        and_(
            and_(
                func.timestampdiff(text("MICROSECOND"), internal_posture_model.c.created_at, external_posture_model.c.created_at) > -microseconds,
                func.timestampdiff(text("MICROSECOND"), internal_posture_model.c.created_at, external_posture_model.c.created_at) < microseconds
            ),
            internal_posture_model.c.user_id == external_posture_model.c.user_id
        )
    ).join(
        user_model,
        internal_posture_model.c.user_id == user_model.c.id
    )
    responces = conn.execute(statement).fetchall()
    result = []
    for res in responces:
        data = res._asdict()
        data["internal_posture_id"] = data.pop("id")
        data["internal_posture_created_at"] = data.pop("created_at")
        data["external_posture_id"] = data.pop("id_1")
        data["external_posture_created_at"] = data.pop("created_at_1")
        data["user_id"] = data.pop("id_2")
        data["user_created_at"] = data.pop("created_at_2")
        result.append(data)

    return result
    