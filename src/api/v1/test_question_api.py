from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.test_question_schema import (
    TestQuestionCreate,
    TestQuestionUpdate,
    TestQuestionResponse,
    TestQuestionListResponse,
    TestQuestionWithoutAnswerResponse,
    TestQuestionWithoutAnswerListResponse,
    LessonAnswer,
    CheckAnswerListResponse,
    LessonEstimateResponse
)
from src.schemas.user_schema import UserRole
from src.services.auth_service import AuthService, get_auth_service
from src.services.test_question_service import TestQuestionService, get_test_question_service
from src.services.user_course_servise import UserCourseService, get_user_course_service
from src.repositories.course import CourseRepository, get_course_repository
from src.repositories.user_course import UserCourseRepository, get_user_course_repository
from src.repositories.lesson import LessonRepository, get_lesson_repository

router = APIRouter(tags=["test_questions"])


@router.get("/", response_model=TestQuestionListResponse, summary="Get all test questions")
async def get_all_test_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Получить все существующие тестовые вопросы
    """
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All test questions are only available to admin",
        )
    
    test_questions = await service.get_all_test_questions(skip, limit)
    total = await service.get_test_questions_count()
    return TestQuestionListResponse(
        questions_list=test_questions,
        total=total,
        skip=skip,
        limit=limit
        )


@router.get("/{test_question_id}", response_model=TestQuestionWithoutAnswerResponse, summary="Get test question by id")
async def get_test_question_by_id(
    test_question_id: UUID,
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Получить тестовый вопрос по ID
    """
    await auth_service.get_current_user()
    test_question = await service.get_test_question_by_id(test_question_id)
    if not test_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test question not found"
        )
    return test_question


@router.post(
    "/create",
    response_model=TestQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new test question"
)
async def create_test_question(
    test_question_data: TestQuestionCreate,
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Создать тестовый вопрос
    """
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test question can only be created by admin",
        )
    
    return await service.create_test_question(test_question_data)


@router.post(
    "/create_multiple",
    response_model=List[TestQuestionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple test questions"
)
async def create_multiple_test_questions(
    test_question_data: List[TestQuestionCreate],
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Создать несколько тестовых вопросов
    """
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test questions can only be created by admin",
        )
    
    return await service.create_multiple_test_questions(test_question_data)


@router.patch("/update/{test_question_id}", response_model=TestQuestionResponse, summary="Update test question by id")
async def update_test_question(
    test_question_id: UUID,
    update_data: TestQuestionUpdate,
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Обновить тестовый вопрос
    """
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test questions can only be updated by admin",
        )
    
    if not await service.test_question_exists(test_question_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test question not found"
        )
    updated_data = await service.update_test_question(test_question_id, update_data)
    if not updated_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update"
        )
    return updated_data


@router.patch("/delete/{test_question_id}",
            summary="Delete test question by id")
async def delete_test_question(
    test_question_id: UUID,
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Удалить тестовый вопрос (мягкое удаление, archived - True)
    """
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test questions can only be deleted by admin",
        )
    await service.delete_test_question(test_question_id)
    return {"message": "Test question deleted successfully"}


@router.get(
    "/lesson/{lesson_id}",
    response_model=TestQuestionWithoutAnswerListResponse,
    summary="Get test questions by lesson id"
)
async def get_test_questions_by_lesson_id(
    lesson_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Получить тест к уроку без ответов (тестовые вопросы отсортированы по порядку)
    """
    await auth_service.get_current_user()
    test_questions = await service.get_test_questions_by_lesson_id(lesson_id)

    return TestQuestionWithoutAnswerListResponse(
        questions_list=test_questions,
        skip=skip,
        limit=limit,
        )


@router.post(
    "/check", 
    response_model=CheckAnswerListResponse, 
    summary="Check answers and update progress"
)
async def check_test(
    user_data: LessonAnswer,
    auth_service: AuthService = Depends(get_auth_service),
    test_service: TestQuestionService = Depends(get_test_question_service),
    db: AsyncSession = Depends(get_session),  # Добавляем прямую зависимость от сессии БД
):
    """
    Проверить ответы на тест и обновить прогресс
    
    Автоматически определяет lesson_id из вопросов
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем ответы
    checked_answers = await test_service.check_test(user_data)
    
    # Если пользователь не студент, просто возвращаем результаты
    if UserRole.student not in current_user.roles:
        return CheckAnswerListResponse(checked_answers=checked_answers)
    
    if not user_data.user_answers:
        return CheckAnswerListResponse(checked_answers=checked_answers)
    
    try:
        # 1. Определяем lesson_id по первому вопросу
        first_question_id = user_data.user_answers[0].uuid
        lesson_id = await test_service.get_lesson_id_by_question_id(first_question_id)
        
        if not lesson_id:
            return CheckAnswerListResponse(
                checked_answers=checked_answers,
                #metadata={"error": "Could not determine lesson from questions"}
            )
        
        # 2. Рассчитываем процент
        total_questions = len(user_data.user_answers)
        correct_answers = sum(1 for item in checked_answers if item.passed)
        percentage = (correct_answers / total_questions) * 100
        
        # 3. Создаем необходимые репозитории
        from src.repositories.user_course import UserCourseRepository
        from src.repositories.lesson import LessonRepository
        from src.repositories.course import CourseRepository
        
        user_course_repo = UserCourseRepository(db)
        lesson_repo = LessonRepository(db)
        course_repo = CourseRepository(db)
        
        # 4. Получаем информацию об уроке
        from src.services.lesson_service import LessonService
        lesson_service = LessonService(lesson_repo)
        
        lesson = await lesson_service.get_by_id(lesson_id, video_only=False)
        course_id = lesson.course_id
        
        # 5. Ищем user_course
        user_course = await user_course_repo.get_by_user_and_course(
            user_id=current_user.uuid,
            course_id=course_id
        )
        
        if user_course:
            # 6. Обновляем прогресс напрямую через репозиторий
            await user_course_repo.update_progress(
                user_course_id=user_course.uuid,
                lesson_id=lesson_id,
                estimate=percentage
            )
            
            return CheckAnswerListResponse(
                checked_answers=checked_answers,
                #metadata={
                    #"lesson_id": str(lesson_id),
                    #"percentage": percentage,
                    #"progress_updated": True
                #}
            )
        else:
            # Если user_course не найден, пользователь не записан на курс
            return CheckAnswerListResponse(
                checked_answers=checked_answers,
                #metadata={
                    #"lesson_id": str(lesson_id),
                    #"percentage": percentage,
                    #"progress_updated": False,
                    #"message": "User not enrolled in course. Start the lesson first."
                #}
            )
            
    except Exception as e:
        # Если что-то пошло не так, все равно возвращаем результаты теста
        return CheckAnswerListResponse(
            checked_answers=checked_answers,
            #metadata={"error": f"Progress update failed: {str(e)}"}
        )

@router.post(
    "/estimate/{lesson_id}", response_model=LessonEstimateResponse, summary="Get estimate by lesson id"
)
async def get_estimate_by_lesson(
    lesson_id: UUID,
    user_data: LessonAnswer,
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Получить оценку к уроку
    """
    await auth_service.get_current_user()
    percentage = await service.get_estimate_by_lesson(lesson_id, user_data)
    return LessonEstimateResponse(
        lesson_id=lesson_id,
        percentage=percentage
    )
