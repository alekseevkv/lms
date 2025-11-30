from typing import Any, List

from fastapi import APIRouter, Depends, Query, status, HTTPException

from src.schemas.test_question_schema import (
    TestQuestionCreate,
    TestQuestionUpdate,
    TestQuestionResponse,
    TestQuestionListResponse,
    TestQuestionWithoutAnswerListResponse,
    LessonAnswer,
    CheckAnswerResponse,
    LessonEstimateResponse,
    TestQuestionSearchParams
)
from src.services.test_question_service import TestQuestionService, get_test_question_service

router = APIRouter(prefix="/test_questions", tags=["test_questions"])


@router.get("/", response_model=TestQuestionListResponse, summary="Получить все тесты")
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TestQuestionService = Depends(get_test_question_service)
):
    test_questions = await service.get_all_test_questions(skip, limit)
    total = await service.get_test_questions_count()
    return TestQuestionListResponse(test_questions=test_questions, total=total, skip=skip, limit=limit)


@router.get("/{test_question_id}", response_model=TestQuestionResponse, summary="Получить тест по ID")
async def get_test_question_by_id(
    test_question_id: Any,
    service: TestQuestionService = Depends(get_test_question_service)
):
    test_questions = await service.get_test_question_by_id(test_question_id)
    if not test_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test question not found"
        )
    return test_questions


@router.post(
    "/create",
    response_model=TestQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тест"
)
async def create_test_question(
    test_question_data: TestQuestionCreate,
    service: TestQuestionService = Depends(get_test_question_service)
):
    return await service.create_test_question(test_question_data)


@router.post(
    "/bulk_create",
    response_model=List[TestQuestionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Cоздать несколько тестов"
)
async def create_multiple_test_questions(
    test_question_data: List[TestQuestionCreate],
    service: TestQuestionService = Depends(get_test_question_service)
):
    return await service.create_multiple_test_questions(test_question_data)


@router.put("/update/{test_question_id}", response_model=TestQuestionResponse, summary="Обновить тест")
async def update_test_question(
    test_question_id: Any,
    update_data: TestQuestionUpdate,
    service: TestQuestionService = Depends(get_test_question_service)
):
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


@router.put("/delete/{test_question_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Удалить тест")
async def delete_test_question(
    test_question_id: Any,
    service: TestQuestionService = Depends(get_test_question_service)
):
    success = await service.delete_test_question(test_question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test question not found"
        )


@router.post(
    "/search", response_model=TestQuestionListResponse, summary="Найти тесты по названию"
)
async def search_test_question_by_name(
    search_params: TestQuestionSearchParams,
    service: TestQuestionService = Depends(get_test_question_service)
):
    test_questions = await service.search_test_question_by_name(
        search_params.name_pattern, search_params.skip, search_params.limit
    )
    total = await service.get_test_questions_count()
    return TestQuestionListResponse(
        test_questions=test_questions,
        total=total,
        skip=search_params.skip,
        limit=search_params.limit,
    )


@router.get(
    "/{lesson_id}",
    response_model=TestQuestionWithoutAnswerListResponse,
    summary="Найти тесты по уроку"
)
async def get_test_questions_by_lesson_id(
    lesson_id: Any,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TestQuestionService = Depends(get_test_question_service)
):
    test_questions = await service.get_test_questions_by_lesson_id(lesson_id, skip, limit)
    total = await service.get_test_questions_count_by_lesson(lesson_id)

    return TestQuestionWithoutAnswerListResponse(
        test_questions=test_questions, total=total, skip=skip, limit=limit
    )


@router.post(
    "/check", response_model=CheckAnswerResponse, summary="Проверить ответы"
)
async def check_test(
    user_data: LessonAnswer,
    service: TestQuestionService = Depends(get_test_question_service)
):
    res = await service.check_test(user_data.user_answers)
    return CheckAnswerResponse(
        uuid=res.uuid,
        passed=res.passed,
        correct_answer=res.correct_answer
    )


@router.post(
    "/estimate/{lesson_id}", response_model=LessonEstimateResponse, summary="Получить оценку за тесты к уроку"
)
async def get_estimate_by_lesson(
    lesson_id: Any,
    user_data: LessonAnswer,
    service: TestQuestionService = Depends(get_test_question_service)
):
    percentage = await service.get_estimate_by_lesson(lesson_id, user_data.user_answers)
    return LessonEstimateResponse(
        lesson_id=lesson_id,
        percentage=percentage
    )
