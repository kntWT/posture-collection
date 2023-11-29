from pydantic import BaseModel, validator
from datetime import datetime

class ExternalPosture(BaseModel):
    id: int
    user_id: int
    neck_angle: float
    torso_angle: float
    created_at: datetime

    @validator("created_at", pre=True)
    def format_timestamp(cls, v: datetime) -> str:
        return v.strftime("%Y-%m-%d_%H:%M:%S.%f")

class ExternalPosturePost(BaseModel):
    user_id: int
    neck_angle: float
    torso_angle: float
    created_at: datetime

class ExternalPostureWithUser(BaseModel):
    id: int
    user_id: int
    neck_angle: float
    torso_angle: float
    created_at: datetime | str
    name: str
    password: str
    internal_posture_calibration_id: int | None
    neck_to_nose_standard: float | None
    neck_angle_offset: float

    @validator("created_at", pre=True)
    def format_timestamp(cls, v: datetime) -> str:
        return v.strftime("%Y-%m-%d_%H:%M:%S.%f")