from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostSchema(BaseModel):
    id: int
    caption: Optional[str]
    scheduled_time: Optional[datetime]
    