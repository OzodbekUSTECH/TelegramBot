from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostSchema(BaseModel):
    id: int
    caption: Optional[str]
    scheduled_time: Optional[datetime]
    is_published: bool = False
    photo_dir = str
    photo_url = str
    video_dir = str
    video_url = str
    button_name = str
    button_url = str
    send_type = Optional[str]
    admin_id = int

    class Config:
        orm_mode = True
    

class CreatePostResponseSchema(BaseModel):
    id: int
    caption: Optional[str]
    scheduled_time: Optional[datetime]
    is_published: bool = False
    photo_dir = str
    photo_url = str
    video_dir = str
    video_url = str
    button_name = str
    button_url = str
    admin_id = int

    class Config:
        orm_mode = True
    