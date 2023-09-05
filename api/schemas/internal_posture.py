from pydantic import BaseModel

class InternalPosture(BaseModel):
    user_id: int
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

class InternalPostureOnlyOrientation(BaseModel):
    orientation_alpha: float
    orientation_beta: float
    orientation_gamma: float

class InternalPostureOnlyEstimation(BaseModel):
    pitch: float
    yaw: float
    roll: float
    nose_x: float
    nose_y: float
    neck_to_nose: float
    standard_dist: float