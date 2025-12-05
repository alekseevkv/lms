from typing import Any, List

from fastapi import APIRouter, Depends, Query, status, HTTPException

from src.schemas.test_question_schema import (
    TestQuestionCreate,
    TestQuestionUpdate,
    TestQuestionResponse,
    TestQuestionListResponse,
    TestQuestionWithoutAnswerListResponse,
    LessonAnswer,
    CheckAnswerListResponse,
    LessonEstimateResponse,
    TestQuestionSearchParams
)
from src.services.test_question_service import TestQuestionService, get_test_question_service

router = APIRouter(prefix="/test_questions", tags=["test_questions"])


@router.get("/", response_model=TestQuestionListResponse, summary="Get all test questions")
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TestQuestionService = Depends(get_test_question_service)
):
    test_questions = await service.get_all_test_questions(skip, limit)
    total = await service.get_test_questions_count()
    return TestQuestionListResponse(
        questions_list=test_questions,
        total=total,
        skip=skip,
        limit=limit
        )


@router.get("/{test_question_id}", response_model=TestQuestionResponse, summary="Get test question by id")
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
    summary="Create a new test question"
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
    summary="Create multiple test questions"
)
async def create_multiple_test_questions(
    test_question_data: List[TestQuestionCreate],
    service: TestQuestionService = Depends(get_test_question_service)
):
    return await service.create_multiple_test_questions(test_question_data)


@router.patch("/update/{test_question_id}", response_model=TestQuestionResponse, summary="Update test question by id")
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


@router.patch("/delete/{test_question_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete test question by id")
async def delete_test_question(
    test_question_id: Any,
    service: TestQuestionService = Depends(get_test_question_service)
):
    success = await service.delete_test_question(test_question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test question not found"
        )
    return {"message": "Test question deleted successfully"}


@router.post(
    "/search", response_model=TestQuestionListResponse, summary="Search test questions by name"
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
        questions_list=test_questions,
        total=total,
        skip=search_params.skip,
        limit=search_params.limit,
    )


@router.get(
    "/lesson/{lesson_id}",
    response_model=TestQuestionWithoutAnswerListResponse,
    summary="Get test questions by lesson id"
)
async def get_test_questions_by_lesson_id(
    lesson_id: Any,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TestQuestionService = Depends(get_test_question_service)
):
    test_questions = await service.get_test_questions_by_lesson_id(lesson_id)

    return TestQuestionWithoutAnswerListResponse(
        questions_list=test_questions,
        skip=skip,
        limit=limit,
        )


@router.post(
    "/check", response_model=CheckAnswerListResponse, summary="Check answers"
)
async def check_test(
    user_data: LessonAnswer,
    service: TestQuestionService = Depends(get_test_question_service)
):
    res = await service.check_test(user_data)
    return CheckAnswerListResponse(checked_answers=res)


@router.post(
    "/estimate/{lesson_id}", response_model=LessonEstimateResponse, summary="Get estimate by lesson id"
)
async def get_estimate_by_lesson(
    lesson_id: Any,
    user_data: LessonAnswer,
    service: TestQuestionService = Depends(get_test_question_service)
):
    percentage = await service.get_estimate_by_lesson(lesson_id, user_data)
    return LessonEstimateResponse(
        lesson_id=lesson_id,
        percentage=percentage
    )
