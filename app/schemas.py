# app/schemas.py
from typing import List, Optional
from pydantic import BaseModel

class SetBase(BaseModel):
    weight: float
    repetitions: int

class SetCreate(SetBase):
    pass

class SetUpdate(SetBase):
    pass

class SetResponse(SetBase):
    id: int

    class Config:
        orm_mode = True

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(ExerciseBase):
    pass

class ExerciseResponse(ExerciseBase):
    id: int
    sets: List[SetResponse] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    token: str

    class Config:
        orm_mode = True