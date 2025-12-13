from typing import Any, List

from fastapi import APIRouter, Depends, Query, status, HTTPException

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
router = APIRouter(prefix="/test_questions", tags=["test_questions"])


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
    test_question_id: Any,
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
    test_question_id: Any,
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
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete test question by id")
async def delete_test_question(
    test_question_id: Any,
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
    lesson_id: Any,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TestQuestionService = Depends(get_test_question_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Получить тест к уроку (тестовые вопросы по порядку, т.е. осортированные по question_num)
    """
    await auth_service.get_current_user()
    test_questions = await service.get_test_questions_by_lesson_id(lesson_id)

    return TestQuestionWithoutAnswerListResponse(
        questions_list=test_questions,
        skip=skip,
        limit=limit,
        )


#@router.post(
#    "/check", response_model=CheckAnswerListResponse, summary="Check answers"
#)

#async def check_test(
#    user_data: LessonAnswer,
#    service: TestQuestionService = Depends(get_test_question_service),
#    auth_service: AuthService = Depends(get_auth_service),
#):
#    await auth_service.get_current_user()
#    res = await service.check_test(user_data)
#    return CheckAnswerListResponse(checked_answers=res)
@router.post(
    "/check", 
    response_model=CheckAnswerListResponse, 
    summary="Check answers and update progress"
)
async def check_test(
    user_data: LessonAnswer,
    auth_service: AuthService = Depends(get_auth_service),
    test_service: TestQuestionService = Depends(get_test_question_service),
    user_course_service: UserCourseService = Depends(get_user_course_service)
):
    """
    Проверить ответы на тест и обновить прогресс пользователя
    
    После проверки автоматически обновляет прогресс по уроку
    Урок считается пройденным при любой отправке теста
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем ответы
    res = await test_service.check_test(user_data)
    
    # Если есть ответы, получаем lesson_id из первого вопроса
    if res and user_data.user_answers:
        # Получаем первый вопрос для определения урока
        first_question_id = user_data.user_answers[0].uuid
        
        # Получаем информацию о вопросе для определения урока
        # (нужно будет добавить метод в репозиторий)
        # Временно получаем lesson_id из параметров запроса или другого источника
        
        # Рассчитываем процент правильных ответов
        total_questions = len(user_data.user_answers)
        correct_answers = sum(1 for item in res if item.passed)
        percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Здесь нужно найти user_course_id для этого урока
        # Для примера, предполагаем, что lesson_id передается в запросе
        # В реальном приложении нужно добавить этот параметр
        
        # Пример обновления прогресса:
        # await user_course_service.update_lesson_progress(
        #     user_course_id=...,
        #     user_id=current_user.uuid,
        #     progress_update=UserCourseProgressUpdate(
        #         lesson_id=lesson_id,
        #         estimate=percentage
        #     )
        # )
    
    return CheckAnswerListResponse(checked_answers=res)

@router.post(
    "/estimate/{lesson_id}", response_model=LessonEstimateResponse, summary="Get estimate by lesson id"
)
async def get_estimate_by_lesson(
    lesson_id: Any,
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
