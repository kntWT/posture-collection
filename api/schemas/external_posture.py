from pydantic import BaseModel

class ExternalPosture(BaseModel):
    id: int
    user_id: int
    internal_posture_id: int | None
    neck_angle: float

class ExternalPosturePost(BaseModel):
    user_id: int
    neck_angle: float

class ExternalPosturePut(BaseModel):
    internal_posture_id: int