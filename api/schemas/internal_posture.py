from pydantic import BaseModel, Field
from datetime import datetime
import json

class InternalPosture(BaseModel):
    id: int
    user_id: int
    file_name: str
    orientation_alpha: float
    orientation_beta: float
    orientation_gamma: float
    pitch: float | None
    yaw: float | None
    roll: float | None
    nose_x: float | None
    nose_y: float | None
    neck_to_nose: float | None
    standard_dist: float | None
    created_at: datetime

class InternalPostureOnlyOrientation(BaseModel):
    user_id: int = Field(alias="userId")
    orientation_alpha: float = Field(alias="alpha")
    orientation_beta: float = Field(alias="beta")
    orientation_gamma: float = Field(alias="gamma")

class InternalPostureOnlyEstimation(BaseModel):
    pitch: float
    yaw: float
    roll: float
    nose_x: float
    nose_y: float
    neck_to_nose: float
    standard_dist: float