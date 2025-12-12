from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.user_course_schema import (
    UserCourseListResponse,
    UserCourseDetailResponse,
    UserCourseResponse,
    UserCourseProgressUpdate,
    StartLessonResponse
)
from src.services.user_course_servise import UserCourseService, get_user_course_service
from src.services.auth_service import AuthService, get_auth_service
from src.schemas.user_schema import UserRole


router = APIRouter(prefix="/user_courses", tags=["user_courses"])


@router.get(
    "/",
    response_model=UserCourseListResponse,
    summary="Get user's courses with progress"
)
async def get_user_courses(
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Получить список курсов пользователя с прогрессом
    
    Возвращает:
    - Список курсов с информацией о прогрессе
    - Общее количество уроков в каждом курсе
    - Количество пройденных уроков
    - Общий прогресс в процентах
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем, что пользователь студент
    if UserRole.student not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access their courses"
        )
    
    return await user_course_service.get_user_courses(current_user.uuid)


@router.get(
    "/{user_course_id}",
    response_model=UserCourseDetailResponse,
    summary="Get detailed user course information"
)
async def get_user_course_detail(
    user_course_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Получить детальную информацию о курсе пользователя
    
    Возвращает:
    - Информацию о курсе
    - Список уроков с прогрессом по каждому уроку
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем, что пользователь студент
    if UserRole.student not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access their courses"
        )
    
    return await user_course_service.get_user_course_detail(
        user_course_id, 
        current_user.uuid
    )


@router.post(
    "/enroll/{course_id}",
    response_model=UserCourseResponse,
    summary="Enroll user in a course",
    status_code=status.HTTP_201_CREATED
)
async def enroll_in_course(
    course_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Записать пользователя на курс
    
    Если пользователь уже записан на курс, возвращает существующую запись
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем, что пользователь студент
    if UserRole.student not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll in courses"
        )
    
    return await user_course_service.enroll_in_course(current_user.uuid, course_id)


@router.post(
    "/{user_course_id}/progress",
    response_model=UserCourseResponse,
    summary="Update lesson progress"
)
async def update_lesson_progress(
    user_course_id: UUID,
    progress_update: UserCourseProgressUpdate,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Обновить прогресс по уроку
    
    Используется после прохождения теста для сохранения оценки
    Урок считается пройденным, если по нему была отправлена оценка (estimate > 0)
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем, что пользователь студент
    if UserRole.student not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can update progress"
        )
    
    return await user_course_service.update_lesson_progress(
        user_course_id,
        current_user.uuid,
        progress_update
    )


@router.post(
    "/lessons/{lesson_id}/start",
    response_model=StartLessonResponse,
    summary="Start a lesson"
)
async def start_lesson(
    lesson_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Начать прохождение урока
    
    Если пользователь не записан на курс, содержащий урок, 
    автоматически записывает его на курс
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем, что пользователь студент
    if UserRole.student not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can start lessons"
        )
    
    return await user_course_service.start_lesson(current_user.uuid, lesson_id)


@router.get(
    "/lessons/{lesson_id}/progress",
    summary="Get user's progress for a specific lesson"
)
async def get_lesson_progress(
    lesson_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Получить прогресс пользователя по конкретному уроку
    
    Возвращает:
    - started: начат ли урок
    - estimate: оценка (если есть)
    - completed: пройден ли урок
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем, что пользователь студент
    if UserRole.student not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can check lesson progress"
        )
    
    return await user_course_service.get_lesson_progress(current_user.uuid, lesson_id)