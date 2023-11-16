from fastapi import File, UploadFile, Body
from datetime import datetime
from fastapi import APIRouter
from models.internal_posture import internal_posture as internal_posture_model
from config.db import conn
from schemas.internal_posture import InternalPosture, InternalPostureOnlyOrientation, InternalPostureOnlyEstimation, InternalPosturePutFilename
from schemas.user import UserId
from sqlalchemy import select, asc, desc, func, text
from typing import List
from util import save_file
from util import JsonParser

internal_posture = APIRouter(prefix="/internal-posture")

@internal_posture.get("/")
async def get_internal_postures() -> List[InternalPosture]:
    return conn.execute(select(internal_posture_model)).fetchall()

@internal_posture.get("/user/{user_id}")
async def get_internal_posutres_by_user_id(user_id: int) -> List[InternalPosture]:
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.user_id==user_id)).fetchall()

@internal_posture.get("/{id}")
async def get_internal_posture_by_id(id: int) -> InternalPosture:
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.id==id)).first()

@internal_posture.get("/filename/{file_name}")
async def get_internal_posture_by_filename(file_name: str) -> InternalPosture:
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.file_name == file_name)).first()

@internal_posture.get("/timestamp/{time}")
async def get_closest_internal_posture_by_timestamp(time: str) -> InternalPosture:
    timestamp: datetime = datetime.strptime(time + "000", "%Y-%m-%d_%H:%M:%S.%f")
    return conn.execute(select(internal_posture_model).
                order_by(asc(func.abs(
                    func.timestampdiff(text("MICROSECOND"), internal_posture_model.c.created_at, timestamp)))
                )).first()

parser = JsonParser(InternalPostureOnlyOrientation)

@internal_posture.post("/")
async def post_internal_posture_only_orientation(orientation: str = Body(...), file: UploadFile = File(...)) -> InternalPosture:
    internal_posture_only_orientation: InternalPostureOnlyOrientation = parser(orientation)
    user_id: int = internal_posture_only_orientation.user_id
    save_file(file, str(user_id))
    conn.execute(internal_posture_model.insert().values(
        **internal_posture_only_orientation.dict(),
        file_name = file.filename,
    ))
    conn.commit()
    return conn.execute(select(internal_posture_model).order_by(desc(internal_posture_model.c.created_at))).first()

@internal_posture.post("/orientation/")
async def post_orientation(orientation: InternalPostureOnlyOrientation) -> InternalPosture:
    conn.execute(internal_posture_model.insert().values(
        **orientation.dict(),
    ))
    conn.commit()
    return conn.execute(select(internal_posture_model).order_by(desc(internal_posture_model.c.created_at))).first()

@internal_posture.post("/video/")
async def post_video(user_id: str = Body(...), file: UploadFile = File(...)) -> int:
    p = JsonParser(UserId)
    usr: UserId = p(user_id)
    uid = usr.id
    save_file(file, str(uid))
    return uid

@internal_posture.put("/{id}")
async def update_estimation(id: int, internal_posture_only_estimation: InternalPostureOnlyEstimation) -> InternalPosture:
    conn.execute(internal_posture_model.update().values(
        **internal_posture_only_estimation.dict()
    ).where(internal_posture_model.c.id==id))
    conn.commit()
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.id==id)).first()

@internal_posture.put("/filename/{id}")
async def update_estimation_by_filename(id: int, file_name: InternalPosturePutFilename) -> InternalPosture:
    conn.execute(internal_posture_model.update().values(
        **file_name.dict()
    ).where(internal_posture_model.c.id==id))
    conn.commit()
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.id==id)).first()