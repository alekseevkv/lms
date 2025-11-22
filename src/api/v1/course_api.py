from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.schemas.course_schema import CourseResponse
from src.services.course_service import CourseService, get_course_service

router = APIRouter()


@router.get(
    "/",
    response_model=list[CourseResponse],
    summary="Get all courses",
)
async def get_all_courses(
    skip: Annotated[int | None, Query(ge=0, description="Entries number to skip")] = 0,
    limit: Annotated[
        int | None, Query(ge=1, le=1000, description="Entries limit")
    ] = 100,
    service: CourseService = Depends(get_course_service),
):
    """
    Get all paginated courses list
    """
    courses = await service.get_all(skip=skip, limit=limit)

    return courses


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Get course by id",
)
async def get_course(
    course_id: UUID, service: CourseService = Depends(get_course_service)
):
    """
    Get course by id
    """
    course = await service.get_by_id(course_id)

    return course
