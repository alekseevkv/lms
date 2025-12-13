from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ReviewBase(BaseModel):
    content: str


class ReviewCreate(ReviewBase):
    course_id: UUID
    #user_id:


class ReviewResponse(ReviewBase):
    uuid: UUID
    user_id: UUID
    course_id: UUID

    model_config = {"from_attributes": True}


class ReviewUpdate(BaseModel):
    content: Optional[str] = None
