from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ReviewBase(BaseModel):
    content: str


class ReviewCreate(ReviewBase):
    course_id: int
    user_id: int


class ReviewResponse(ReviewBase):
    uuid: UUID
    user_id: int
    course_id: int

    model_config = {"from_attributes": True}


class ReviewUpdate(BaseModel):
    content: Optional[str] = None
