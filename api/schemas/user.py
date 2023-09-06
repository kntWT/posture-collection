from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    neck_to_nose_standard: float | None
    created_at: datetime

class UserPost(BaseModel):
    name: str
    neck_to_nose_standard: Optional[float]

class UserPut(BaseModel):
    neck_to_nose_standard: float