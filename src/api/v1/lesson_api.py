from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException

from src.schemas.lesson_schema import (
    LessonResponse,
    LessonCreate,
    LessonUpdate,
    LessonVideoResponse
)
from src.schemas.user_schema import UserRole
from src.services.auth_service import AuthService, get_auth_service
from src.services.lesson_service import LessonService, get_lesson_service

router = APIRouter(tags=["lessons"])


@router.get(
    "/get/{lesson_id}",
    response_model=LessonResponse | LessonVideoResponse,
    summary="Get lesson by id",
    description="Get lesson information. Use query parameter 'video_only=true' to get only video information."
)
async def get_lesson(
    lesson_id: UUID,
    video_only: Annotated[
        bool, 
        Query(
            description="If true, returns only video information (uuid, name, video_url)"
        )
    ] = False,
    service: LessonService = Depends(get_lesson_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get lesson by id
    
    - **lesson_id**: UUID of the lesson
    - **video_only**: If true, returns only video URL and basic info
    """
    current_user = await auth_service.get_current_user()
    lesson = await service.get_by_id(lesson_id, video_only=video_only)
    return lesson


@router.get(
    "/get_all/{course_id}",
    response_model=list[LessonResponse],
    summary="Get all lessons for course",
)
async def get_course_lessons(
    course_id: UUID,
    skip: Annotated[int | None, Query(ge=0, description="Entries number to skip")] = 0,
    limit: Annotated[
        int | None, Query(ge=1, le=1000, description="Entries limit")
    ] = 100,
    service: LessonService = Depends(get_lesson_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get all lessons for a specific course
    """
    current_user = await auth_service.get_current_user()
    lessons = await service.get_all_by_course(course_id, skip=skip, limit=limit)
    return lessons


@router.post(
    "/create/",
    response_model=LessonResponse,
    summary="Create new lesson",
    status_code=201,
)
async def create_lesson(
    lesson_data: LessonCreate,
    service: LessonService = Depends(get_lesson_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Create a new lesson
    """
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can create lessons",
        )
    lesson = await service.create_lesson(lesson_data)
    return lesson


@router.put(
    "/update/{lesson_id}",
    response_model=LessonResponse,
    summary="Update lesson",
)
async def update_lesson(
    lesson_id: UUID,
    update_data: LessonUpdate,
    service: LessonService = Depends(get_lesson_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Update lesson information
    """
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can update lessons",
        )
    lesson = await service.update_lesson(lesson_id, update_data)
    return lesson


@router.delete(
    "/{lesson_id}",
    status_code=204,
    summary="Delete lesson (soft delete)",
)
async def delete_lesson(
    lesson_id: UUID,
    service: LessonService = Depends(get_lesson_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Delete lesson (soft delete - sets archived flag to True)
    """
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can delete lessons",
        )
    await service.delete_lesson(lesson_id)