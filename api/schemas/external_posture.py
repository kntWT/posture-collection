from pydantic import BaseModel
from datetime import datetime

class ExternalPosture(BaseModel):
    id: int
    user_id: int
    neck_angle: float
    torso_angle: float
    created_at: datetime

class ExternalPosturePost(BaseModel):
    user_id: int
    neck_angle: float
    torso_angle: float
    created_at: datetime