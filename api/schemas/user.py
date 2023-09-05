from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    neck_to_nose_standard: float | None

class UserPost(BaseModel):
    name: str
    neck_to_nose_standard: Optional[float]

class UserPut(BaseModel):
    neck_to_nose_standard: float