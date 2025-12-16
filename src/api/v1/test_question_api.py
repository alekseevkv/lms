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
@router.post(
    "/check", 
    response_model=CheckAnswerListResponse, 
    summary="Check answers and update progress"
)
async def check_test(
    user_data: LessonAnswer,
    auth_service: AuthService = Depends(get_auth_service),
    test_service: TestQuestionService = Depends(get_test_question_service),
    db: AsyncSession = Depends(get_session),
):
    """
    Проверить ответы на тест и обновить прогресс с детализацией по вопросам
    
    Сохраняет прогресс в формате: [{lesson_id: [{question_id: estimate}]}]
    где estimate = 100 (правильный ответ) или 0 (неправильный ответ)
    
    ВАЖНО: Если пользователь уже отвечал на вопрос, повторная проверка не производится.
    Проверяется только первый ответ.
    """
    current_user = await auth_service.get_current_user()
    
    # Проверяем ответы
    checked_answers = await test_service.check_test(user_data)
    
    if not user_data.user_answers:
        return CheckAnswerListResponse(checked_answers=checked_answers)
    
    try:
        # Определяем lesson_id по первому вопросу
        first_question_id = user_data.user_answers[0].uuid
        lesson_id = await test_service.get_lesson_id_by_question_id(first_question_id)
        
        if not lesson_id:
            return CheckAnswerListResponse(checked_answers=checked_answers)
        
        # Проверяем, что все вопросы принадлежат одному уроку
        await test_service.validate_questions_belong_to_same_lesson(
            [answer.uuid for answer in user_data.user_answers]
        )
        
        # Создаем необходимые репозитории
        from src.repositories.user_course import UserCourseRepository
        from src.repositories.lesson import LessonRepository
        from src.repositories.course import CourseRepository
        from src.repositories.test_question import TestQuestionRepository
        user_course_repo = UserCourseRepository(db)
        lesson_repo = LessonRepository(db)
        course_repo = CourseRepository(db)
        test_question_repo = TestQuestionRepository(db)
        # Получаем информацию об уроке
        from src.services.lesson_service import LessonService
        lesson_service = LessonService(lesson_repo)
        
        lesson = await lesson_service.get_by_id(lesson_id, video_only=False)
        course_id = lesson.course_id
        
        # Ищем user_course
        user_course = await user_course_repo.get_by_user_and_course(
            user_id=current_user.uuid,
            course_id=course_id
        )
        
        if user_course:
            # Получаем текущий прогресс по уроку
            current_progress = await user_course_repo.get_lesson_progress(
                user_course.uuid,
                lesson_id
            )
            
            # Фильтруем вопросы, на которые пользователь уже отвечал
            already_answered_questions = set()
            new_question_progress = []
            
            if current_progress and current_progress.get("questions"):
                # Собираем ID вопросов, на которые уже есть ответы
                for qp in current_progress["questions"]:
                    if isinstance(qp, dict) and qp.get("question_id"):
                        q_id = qp.get("question_id")
                        if isinstance(q_id, str):
                            try:
                                already_answered_questions.add(UUID(q_id))
                            except:
                                pass
                        elif isinstance(q_id, UUID):
                            already_answered_questions.add(q_id)
            
            # Создаем прогресс по новым вопросам
            # Сопоставляем ответы пользователя с проверенными результатами
            user_answers_dict = {answer.uuid: answer.user_answer for answer in user_data.user_answers}
            checked_answers_dict = {item.uuid: item for item in checked_answers}
            
            for question_id, user_answer in user_answers_dict.items():
                # Проверяем, отвечал ли пользователь уже на этот вопрос
                if question_id in already_answered_questions:
                    continue  # Пропускаем вопросы, на которые уже отвечали
                
                checked_item = checked_answers_dict.get(question_id)
                if checked_item:
                    # Определяем оценку: 100 за правильный ответ, 0 за неправильный
                    estimate = 100.0 if checked_item.passed else 0.0
                    
                    new_question_progress.append({
                        "question_id": question_id,
                        "estimate": estimate,
                        "user_answer": user_answer,
                        "correct_answer": checked_item.correct_answer
                    })
            
            # Если есть новые ответы, обновляем прогресс
            if new_question_progress:
                await user_course_repo.update_progress(
                    user_course_id=user_course.uuid,
                    lesson_id=lesson_id,
                    question_progress=new_question_progress
                )
                
                # Получаем обновленный прогресс для ответа
                updated_progress = await user_course_repo.get_lesson_progress(
                    user_course_id=user_course.uuid,
                    lesson_id=lesson_id
                )
                
                # Добавляем информацию о новых ответах в результат
                response_data = CheckAnswerListResponse(
                    checked_answers=checked_answers,
                )
                
                # Добавляем информацию о том, какие вопросы были пропущены (уже отвечены)
                if already_answered_questions:
                    response_data.already_answered = list(already_answered_questions)
                    response_data.new_questions_answered = [qp["question_id"] for qp in new_question_progress]
                    response_data.message = f"Пропущено {len(already_answered_questions)} уже отвеченных вопросов. Добавлено {len(new_question_progress)} новых ответов."
                
                return response_data
            else:
                # Если нет новых ответов (все вопросы уже были отвечены)
                return CheckAnswerListResponse(
                    checked_answers=checked_answers,
                    message="Все вопросы уже были отвечены ранее. Прогресс не обновлен.",
                    already_answered=list(already_answered_questions)
                )
        else:
            # Если user_course не найден, создаем его
            from src.services.user_course_servise import UserCourseService
            user_course_service_full = UserCourseService(
                user_course_repo=user_course_repo,
                course_repo=course_repo,
                lesson_repo=lesson_repo,
                test_question_repo= test_question_repo
            )
            
            # Записываем пользователя на курс
            new_user_course = await user_course_service_full.enroll_in_course(
                user_id=current_user.uuid,
                course_id=course_id
            )
            
            # Создаем прогресс по всем вопросам (первый раз)
            question_progress = []
            for answer in user_data.user_answers:
                checked_item = next((item for item in checked_answers if item.uuid == answer.uuid), None)
                if checked_item:
                    estimate = 100.0 if checked_item.passed else 0.0
                    question_progress.append({
                        "question_id": answer.uuid,
                        "estimate": estimate,
                        "user_answer": answer.user_answer,
                        "correct_answer": checked_item.correct_answer
                    })
            
            # Затем обновляем прогресс
            await user_course_repo.update_progress(
                user_course_id=new_user_course.uuid,
                lesson_id=lesson_id,
                question_progress=question_progress
            )
            
            return CheckAnswerListResponse(
                checked_answers=checked_answers,
                message="Курс создан и прогресс сохранен."
            )
            
    except Exception as e:
        # Если что-то пошло не так, все равно возвращаем результаты теста
        import traceback
        print(f"Error in check_test: {str(e)}")
        print(traceback.format_exc())
        
        return CheckAnswerListResponse(
            checked_answers=checked_answers,
            error_message=f"Произошла ошибка при обновлении прогресса: {str(e)}"
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
