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
    is_superuser: bool = False
    created_at: datetime

    class Config:
        orm_mode = True

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True

class AdminUpdateSchema(BaseModel):
    tg_id: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    channel_id: Optional[int] = None
    is_superuser: Optional[bool] = False
    
    # class Config:
    #     orm_mode = True

class UpdateOwnAdminSchema(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    channel_id: Optional[int] = None

    # class Config:
    #     orm_mode = True

class UpdateOwnAdminDataReponse(BaseModel):
    id: int
    tg_id: Optional[int]
    email: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    channel_id: Optional[int]
    is_superuser: bool = False
    created_at: datetime

    class Config:
        orm_mode = True