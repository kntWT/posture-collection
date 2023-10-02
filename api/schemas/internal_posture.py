from pydantic import BaseModel, Field
from datetime import datetime

class InternalPosture(BaseModel):
    id: int
    user_id: int
    file_name: str
    orientation_alpha: float | None
    orientation_beta: float | None
    orientation_gamma: float | None
    pitch: float | None
    yaw: float | None
    roll: float | None
    nose_x: float | None
    nose_y: float | None
    neck_x: float | None
    neck_y: float | None
    neck_to_nose: float | None
    standard_dist: float | None
    calibrate_flag: bool
    created_at: datetime

class InternalPostureOnlyOrientation(BaseModel):
    user_id: int = Field(alias="userId")
    orientation_alpha: float | None = Field(alias="alpha")
    orientation_beta: float | None = Field(alias="beta")
    orientation_gamma: float | None = Field(alias="gamma")
    calibrate_flag: bool = Field(alias="calibrateFlag")
    created_at: datetime | str = Field(alias="createdAt")

class InternalPostureOnlyEstimation(BaseModel):
    pitch: float
    yaw: float
    roll: float
    nose_x: float
    nose_y: float
    neck_x: float
    neck_y: float
    neck_to_nose: float
    standard_dist: float