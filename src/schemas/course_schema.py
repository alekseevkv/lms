from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CourseBase(BaseModel):
    name: str
    desc: str | None


class CourseResponse(CourseBase):
    uuid: UUID

    model_config = {"from_attributes": True}

class CourseUpdate(CourseBase):
    name: Optional[str] = None
    desc: Optional[str] = None