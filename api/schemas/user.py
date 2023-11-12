from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    password: str
    internal_posture_calibration_id: int | None
    neck_to_nose_standard: float | None
    neck_angle_offset: float
    created_at: datetime

class UserPost(BaseModel):
    name: str
    password: str

class UserCalibrateInternalPosture(BaseModel):
    internal_posture_calibration_id: int
    neck_to_nose_standard: Optional[float | None]

class UserCalibrateExternalPosture(BaseModel):
    neck_angle_offset: float