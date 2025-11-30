from fastapi import APIRouter, Depends
from uuid import UUID

from src.schemas.course_schema import CourseBase,CourseUpdate
from src.services.course_service import CourseService, get_course_service

router = APIRouter()

@router.post("/course", summary="Create a new course")
async def add_course(
    course_date: CourseBase,
    service: CourseService = Depends(get_course_service),
):
    res = await service.create_course(course_date)

    return res

@router.patch("/course/{course_id}/update", summary="Update a course by id")
async def update_course(
    course_id: UUID,
    course_date: CourseUpdate,
    service: CourseService = Depends(get_course_service)
):
    res = await service.update_course(course_id, course_date)

    return res

@router.patch("/course/{course_id}/delete", summary="Delete a course by id")
async def delete_course(
    course_id: UUID,
    service: CourseService = Depends(get_course_service)
):
    await service.delete_course(course_id)
    return {"message": "Course delete successfully"}

