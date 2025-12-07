from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.models.user import User
from src.schemas.user_course_schema import (
    CourseWithProgressResponse,
    UserCourseDetailedResponse,
    UserCourseResponse,
    UserCourseCreate,
    StartLessonResponse,
    CompleteLessonRequest
)
from src.services.auth_service import AuthService, get_auth_service
from src.services.user_course_servise import UserCourseService, get_user_course_service

router = APIRouter(prefix="/user_courses", tags=["user-courses"])


@router.get(
    "/",
    response_model=List[CourseWithProgressResponse],
    summary="Get user courses with progress"
)
async def get_user_courses(
    skip: Annotated[int | None, Query(ge=0, description="Entries number to skip")] = 0,
    limit: Annotated[
        int | None, Query(ge=1, le=1000, description="Entries limit")
    ] = 100,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service),
):
    """
    Get all courses for current user with progress information
    
    Returns list of courses with user's progress in each course
    """
    current_user = await auth_service.get_current_user()
    
    courses = await user_course_service.get_user_courses(
        current_user.uuid, skip=skip, limit=limit
    )
    return courses


@router.get(
    "/{user_course_id}",
    response_model=UserCourseDetailedResponse,
    summary="Get user course details"
)
async def get_user_course(
    user_course_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service),
):
    """
    Get detailed information about user's course
    
    Returns:
    - User course information
    - Course details
    - List of lessons with progress for each lesson
    """
    current_user = await auth_service.get_current_user()
    
    course_data = await user_course_service.get_user_course_by_id(
        user_course_id, current_user
    )
    return course_data


@router.post(
    "/enroll/{course_id}",
    response_model=UserCourseResponse,
    summary="Enroll in a course",
    status_code=status.HTTP_201_CREATED
)
async def enroll_in_course(
    course_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service),
):
    """
    Enroll current user in a course
    
    Creates a new user_course record with initial progress
    """
    current_user = await auth_service.get_current_user()
    
    user_course = await user_course_service.enroll_in_course(course_id, current_user)
    return user_course


@router.post(
    "/lessons/{lesson_id}/start",
    response_model=StartLessonResponse,
    summary="Start a lesson"
)
async def start_lesson(
    lesson_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service),
):
    """
    Mark a lesson as started for current user
    
    Returns the lesson with progress information
    """
    current_user = await auth_service.get_current_user()
    
    result = await user_course_service.start_lesson(lesson_id, current_user)
    return result


@router.post(
    "/lessons/{lesson_id}/complete",
    summary="Complete a lesson with test results"
)
async def complete_lesson(
    lesson_id: UUID,
    request: CompleteLessonRequest,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service),
):
    """
    Complete a lesson with test estimate
    
    Lesson is considered completed when test is submitted (regardless of answers)
    
    - **estimate**: Optional score from 0 to 100
    """
    current_user = await auth_service.get_current_user()
    
    result = await user_course_service.complete_lesson(lesson_id, request, current_user)
    return result


@router.get(
    "/stats/my",
    summary="Get user course statistics"
)
async def get_user_course_stats(
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service),
):
    """
    Get statistics about user's courses progress
    
    Returns:
    - Total courses
    - Completed courses
    - Courses in progress
    - Average progress
    """
    current_user = await auth_service.get_current_user()
    
    stats = await user_course_service.get_user_course_stats(current_user.uuid)
    return stats