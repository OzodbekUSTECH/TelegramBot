from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostSchema(BaseModel):
    id: int
    caption: Optional[str]
    scheduled_time: Optional[datetime]
    is_published: bool = False
    photo_dir = Optional[str]
    photo_url = Optional[str]
    video_dir = Optional[str]
    video_url = Optional[str]
    button_name = Optional[str]
    button_url = Optional[str]
    send_type = Optional[str]
    admin_id = int

    class Config:
        orm_mode = True
    

class CreatePostResponseSchema(BaseModel):
    id: int
    caption: Optional[str]
    scheduled_time: Optional[datetime]
    is_published: bool = False
    photo_dir = Optional[str]
    photo_url = Optional[str]
    video_dir = Optional[str]
    video_url = Optional[str]
    button_name = Optional[str]
    button_url = Optional[str]
    admin_id = int

    class Config:
        orm_mode = True
    