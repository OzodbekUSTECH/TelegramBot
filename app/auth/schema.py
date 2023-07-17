from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TokenData(BaseModel):
    email: str


class AdminCreateSchema(BaseModel):
    tg_id: int
    email: str
    password: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    channel_id: Optional[int]
    is_superuser: bool = False
    
    class Config:
        orm_mode = True

class AdminSchema(BaseModel):
    id: int
    tg_id: int
    email: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    channel_id: Optional[int]
    is_superuser: bool
    created_at: datetime

    class Config:
        orm_mode = True

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True