from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, HttpUrl


class LessonBase(BaseModel):
    name: str
    desc: Optional[str] = None
    content: str
    video_url: Optional[HttpUrl] = None
    course_id: UUID


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[HttpUrl] = None


class LessonResponse(LessonBase):
    uuid: UUID
    create_at: datetime
    update_at: datetime
    archived: bool

    model_config = {"from_attributes": True}


class LessonVideoResponse(BaseModel):
    uuid: UUID
    name: str
    video_url: Optional[str] = None
    
    model_config = {"from_attributes": True}