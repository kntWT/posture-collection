from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    password: str
    neck_to_nose_standard: float | None
    created_at: datetime

class UserPost(BaseModel):
    name: str
    password: str

class UserPut(BaseModel):
    neck_to_nose_standard: float