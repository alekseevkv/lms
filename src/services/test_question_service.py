from typing import List, Optional, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.repositories.test_question import TestQuestionRepository, get_test_question_repository
from src.schemas.test_question_schema import (
    TestQuestionCreate,
    TestQuestionUpdate,
    TestQuestionResponse,
    TestQuestionWithoutAnswerResponse,
    CheckAnswerResponse,
    LessonAnswer
)


class TestQuestionService:
    def __init__(self, repo: TestQuestionRepository):
        self.repo = repo

    async def get_test_question_by_id(self, test_question_id: Any) -> TestQuestionWithoutAnswerResponse:
        '''Получить тест по ID'''
        test_question = await self.repo.get_by_id(test_question_id)
        if not test_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test question not found",
            )
        return TestQuestionWithoutAnswerResponse.model_validate(test_question)

    async def get_all_test_questions(
        self, skip: int = 0, limit: int = 100
    ) -> List[TestQuestionResponse]:
        '''Получить все тесты'''
        test_questions = await self.repo.get_all(skip, limit)
        if not test_questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        return [TestQuestionResponse.model_validate(test_question) for test_question in test_questions]

    async def create_test_question(self, test_question_data: TestQuestionCreate) -> TestQuestionResponse:
        '''Создать новый тест'''
        test_question_dict = test_question_data.model_dump()
        test_question = await self.repo.create(test_question_dict)
        return TestQuestionResponse.model_validate(test_question)

    async def create_multiple_test_questions(
        self, test_questions_data: List[TestQuestionCreate]
    ) -> List[TestQuestionResponse]:
        '''Создать несколько тестов'''
        test_questions_dict = [
            test_question_data.model_dump() for test_question_data in test_questions_data]
        test_questions = await self.repo.create_many(test_questions_dict)
        return [TestQuestionResponse.model_validate(test_question) for test_question in test_questions]

    async def update_test_question(
        self, test_question_id: Any, update_data: TestQuestionUpdate
    ) -> Optional[TestQuestionResponse]:
        '''Обновить тест'''
        update_dict = {
            k: v for k, v in update_data.model_dump().items() if v is not None
        }
        if not update_dict:
            return None
        test_question = await self.repo.update(test_question_id, update_dict)
        if not test_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test question not found",
            )
        return TestQuestionResponse.model_validate(test_question)

    async def delete_test_question(self, test_question_id: Any) -> None:
        '''Удалить тест'''
        res = await self.repo.delete(test_question_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test question not found",
            )
    

    async def search_test_question_by_name(self, name_pattern: str, skip: int, limit: int) -> List[TestQuestionResponse]:
        '''Поиск тестов по названию'''
        test_questions = await self.repo.search_by_name(name_pattern, skip, limit)
        if not test_questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test question not found",
            )
        return [TestQuestionResponse.model_validate(test_question) for test_question in test_questions]

    async def get_test_questions_by_lesson_id(self, lesson_id: Any) -> List[TestQuestionWithoutAnswerResponse]:
        '''Получить тесты для урока'''
        test_questions = await self.repo.get_by_lesson_id(lesson_id)
        if not test_questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        return [TestQuestionWithoutAnswerResponse.model_validate(test_question) for test_question in test_questions]

    async def get_test_questions_count(self) -> int | None:
        '''Получить общее количество тестов'''
        res = await self.repo.get_count()
        return res

    async def get_test_questions_count_by_lesson(self, lesson_id: Any) -> int | None:
        '''Получить количество тестов в уроке'''
        res = await self.repo.get_count_by_lesson(lesson_id)
        return res

    async def check_test_question(self, test_question_id: Any, user_answer: str) -> bool:
        '''Проверить ответ пользователя на вопрос'''
        res = await self.repo.check_answer(test_question_id, user_answer)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        return res

    async def check_test(self, user_answers: LessonAnswer) -> List[CheckAnswerResponse]:
        '''Проверить ответ пользователя на тест'''
        answers = []
        for ans in user_answers.user_answers:
            answers.append(ans.model_dump())
        res = await self.repo.bulk_check_answers(answers)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        check = []
        for result in res:
            check.append(CheckAnswerResponse.model_validate(result))
        return check

    async def get_estimate_by_lesson(self, lesson_id: Any, user_answers: LessonAnswer) -> float:
        '''Получить оценку за тест к уроку'''
        answers = []
        for ans in user_answers.user_answers:
            answers.append(ans.model_dump())
        percentage = await self.repo.calculate_estimate(lesson_id, answers)
        if not percentage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        return percentage

    async def test_question_exists(self, test_question_id: Any) -> bool:
        '''Проверить существование теста'''
        return await self.repo.exists_by_id(test_question_id)

    # новое
    async def get_lesson_id_by_question_id(self, question_id: UUID) -> Optional[UUID]:
        """Получить ID урока по ID вопроса"""
        return await self.repo.get_lesson_id_by_question_id(question_id)

    async def get_lesson_ids_by_question_ids(self, question_ids: List[UUID]) -> List[UUID]:
        """Получить ID уроков по списку ID вопросов"""
        return await self.repo.get_lesson_ids_by_question_ids(question_ids)

    async def validate_questions_belong_to_same_lesson(self, question_ids: List[UUID]) -> UUID:
        """
        Проверить, что все вопросы принадлежат одному уроку
        Возвращает ID урока, если все вопросы из одного урока
        """
        lesson_ids = await self.get_lesson_ids_by_question_ids(question_ids)
        
        if not lesson_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No questions found",
            )
        
        if len(lesson_ids) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Questions belong to different lessons: {lesson_ids}",
            )
        
        return lesson_ids[0]
async def get_test_question_service(
    repo: TestQuestionRepository = Depends(get_test_question_repository),
) -> TestQuestionService:
    return TestQuestionService(repo)
