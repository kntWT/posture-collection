from fastapi import File, UploadFile, Body
# from datetime import datetime
import datetime
from fastapi import APIRouter
from models.internal_posture import internal_posture as internal_posture_model
from config.db import conn
from schemas.internal_posture import InternalPosture, InternalPostureOnlyOrientation, InternalPostureOnlyEstimation, InternalPosturePutFilename
from schemas.user import UserId
from sqlalchemy import select, asc, desc, func, text, between, and_
from sqlalchemy.sql.expression import bindparam
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
    return conn.execute(select(internal_posture_model).
                with_hint(internal_posture_model, "FORCE INDEX (file_name_index)", 'mysql').
                where(internal_posture_model.c.file_name == file_name)).first()

@internal_posture.get("/timestamp/{time}")
async def get_closest_internal_posture_by_timestamp(time: str) -> InternalPosture:
    timestamp: datetime.datetime = datetime.datetime.strptime(time + "000", "%Y-%m-%d_%H:%M:%S.%f")
    return conn.execute(select(internal_posture_model).
                # with_hint(internal_posture_model, "FORCE INDEX (created_at_index)", 'mysql').
                filter(between(internal_posture_model.c.created_at, timestamp - datetime.timedelta(microseconds=40000), timestamp + datetime.timedelta(microseconds=40000))).
                order_by(asc(func.abs(
                    func.timestampdiff(text("MICROSECOND"), internal_posture_model.c.created_at, timestamp)))
                )).first()

@internal_posture.get("/timestamp/list/{start_time}/{limit}")
async def get_internal_posture_list_from_start_time(start_time: str, limit: int) -> List[InternalPosture]:
    first_data: InternalPosture = await get_closest_internal_posture_by_timestamp(start_time)
    if first_data is None:
        return []
    first_id: int = first_data.id
    return conn.execute(select(internal_posture_model).
                filter(and_(internal_posture_model.c.id >= first_id, internal_posture_model.c.calibrate_flag == False)).
                # order_by(asc(internal_posture_model.c.created_at)).
                order_by(asc(internal_posture_model.c.id)).
                limit(limit)
            ).fetchall()

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
    return conn.execute(select(internal_posture_model).filter(internal_posture_model.c.created_at==internal_posture_only_orientation.created_at)).first()

@internal_posture.post("/orientation/")
async def post_orientation(orientation: InternalPostureOnlyOrientation) -> InternalPosture:
    conn.execute(internal_posture_model.insert().values(
        **orientation.dict(),
    ))
    conn.commit()
    return conn.execute(select(internal_posture_model).filter(internal_posture_model.c.created_at==orientation.created_at)).first()

@internal_posture.post("/orientation/list/")
async def post_internal_posture_only_orientation_list(orientations: List[InternalPostureOnlyOrientation]) -> List[InternalPosture]:
    if len(orientations) <= 0:
        return []
    conn.execute(internal_posture_model.insert().values(
        [orientation.dict() for orientation in orientations]
    ))
    conn.commit()
    return conn.execute(select(internal_posture_model).filter(internal_posture_model.c.created_at in [o.created_at for o in orientations])).fetchall()

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

@internal_posture.put("/list/")
async def update_estimations(internal_posture_only_estimations: List[InternalPostureOnlyEstimation]) -> List[InternalPosture]:
    if len(internal_posture_only_estimations) <= 0:
        return []
    stmt = internal_posture_model.update().values(
        {key: bindparam(key) for key in internal_posture_only_estimations[0].dict().keys()}
    ).where(internal_posture_model.c.id==bindparam("id"))
    conn.execute(stmt, [estimation.dict() for estimation in internal_posture_only_estimations])
    conn.commit()
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.id in [e.id for e in internal_posture_only_estimations])).fetchall()

@internal_posture.put("/filename/{id}")
async def update_estimation_by_filename(id: int, file_name: InternalPosturePutFilename) -> InternalPosture:
    conn.execute(internal_posture_model.update().values(
        **file_name.dict()
    ).where(internal_posture_model.c.id==id))
    conn.commit()
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.id==id)).first()

@internal_posture.put("/filename/list/")
async def update_estimations_by_filename(file_names: List[InternalPosturePutFilename]) -> List[InternalPosture]:
    if len(file_names) <= 0:
        return []
    stmt = internal_posture_model.update().values(
        {key: bindparam(key) for key in file_names[0].dict().keys()}
    ).where(internal_posture_model.c.id==bindparam("id"))
    conn.execute(stmt, [file_name.dict() for file_name in file_names])
    conn.commit()
    return conn.execute(select(internal_posture_model).where(internal_posture_model.c.id in [f.id for f in file_names])).fetchall()