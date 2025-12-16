from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

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


router = APIRouter(tags=["user_courses"])

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
    #if UserRole.student not in current_user.roles:
        #raise HTTPException(
            #status_code=status.HTTP_403_FORBIDDEN,
            #detail="Only students can access their courses"
        #)
    
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
    
    return await user_course_service.enroll_in_course(current_user.uuid, course_id)

@router.put(
    "/{user_course_id}/lessons/{lesson_id}/questions/{question_id}",
    response_model=UserCourseResponse,
    summary="Update question progress"
)
async def update_question_progress(
    user_course_id: UUID,
    lesson_id: UUID,
    question_id: UUID,
    estimate: float = Query(..., description="Estimate value (0 or 100)"),
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Обновить оценку для конкретного вопроса в уроке
    """
    current_user = await auth_service.get_current_user()
    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can create update progress",
        )
    return await user_course_service.update_question_progress(
        user_course_id,
        lesson_id,
        question_id,
        estimate
    )

@router.patch(
    "/{user_course_id}/reset-progress",
    response_model=UserCourseResponse,
    summary="Reset user course progress",
    description="Сбрасывает прогресс пользователя по курсу (progress = []). " 
)
async def reset_user_course_progress(
    user_course_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Сбросить прогресс пользователя по курсу
    
    Устанавливает progress = [], как будто пользователь только записался на курс.
    
    """
    current_user = await auth_service.get_current_user()
    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can create update progress",
        )
    
    return await user_course_service.reset_user_course_progress(user_course_id)

@router.post(
    "/lessons/{lesson_id}/start",
    response_model=StartLessonResponse,
    summary="Start a lesson"
)

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
    
    return await user_course_service.get_lesson_progress(current_user.uuid, lesson_id)

@router.patch(
    "/{user_course_id}/soft-delete",
    response_model=UserCourseResponse,
    summary="Soft delete user course (admin only)",
    description="Мягкое удаление user_course. Устанавливает archived=True. Только для администраторов."
)
async def soft_delete_user_course(
    user_course_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Мягкое удаление user_course
    
    ТОЛЬКО для администраторов. Студенты не могут удалять свои курсы.
    Устанавливает флаг archived=True вместо физического удаления.
    """
    current_user = await auth_service.get_current_user()
    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can create update progress",
        )

    
    return await user_course_service.soft_delete_user_course(
        user_course_id,
        current_user.uuid
    )