from typing import List, Optional, Any, Dict

from fastapi import Depends, HTTPException, status

from src.repositories.test_question import TestQuestionRepository, get_test_question_repository
from src.schemas.test_question_schema import (
    TestQuestionCreate,
    TestQuestionUpdate,
    TestQuestionResponse,
    TestQuestionListResponse,
    TestQuestionWithoutAnswerListResponse,
    CheckAnswerResponse,
    LessonEstimateResponse
)


class TestQuestionService:
    def __init__(self, repo: TestQuestionRepository):
        self.repo = repo

    async def get_test_question_by_id(self, test_question_id: Any) -> Optional[TestQuestionResponse]:
        '''Получить тест по ID'''
        test_question = await self.repo.get_by_id(test_question_id)
        if not test_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test question not found",
            )
        return test_question

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
        return [test_question for test_question in test_questions]

    async def create_test_question(self, test_question_data: TestQuestionCreate) -> TestQuestionResponse:
        '''Создать новый тест'''
        test_question_dict = test_question_data.model_dump()
        test_question = await self.repo.create(test_question_dict)
        return test_question

    async def create_multiple_test_questions(
        self, test_questions_data: List[TestQuestionCreate]
    ) -> List[TestQuestionResponse]:
        '''Создать несколько тестов'''
        test_questions_dict = [
            test_question_data.model_dump for test_question_data in test_questions_data]
        test_questions = await self.repo.create_many(test_questions_dict)
        return [test_question for test_question in test_questions]

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
        return test_question

    async def delete_test_question(self, test_question_id: Any) -> bool:
        '''Удалить тест'''
        return await self.repo.delete(test_question_id)

    async def search_test_question_by_name(self, name_pattern: str, skip: int, limit: int) -> TestQuestionListResponse:
        '''Поиск тестов по названию'''
        test_questions = await self.repo.search_by_name(name_pattern, skip, limit)
        if not test_questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test question not found",
            )
        return [test_question for test_question in test_questions]

    async def get_test_questions_by_lesson_id(self, lesson_id: Any) -> TestQuestionWithoutAnswerListResponse:
        '''Получить тесты для урока'''
        test_questions = await self.repo.get_by_lesson_id(lesson_id)
        if not test_questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        return [test_question for test_question in test_questions]

    async def get_test_questions_count(self) -> int:
        '''Получить общее количество тестов'''
        res = await self.repo.get_count()
        return res

    async def get_test_questions_count_by_lesson(self, lesson_id: Any) -> int:
        '''Получить количество тестов в уроке'''
        res = await self.repo.get_count_by_lesson(lesson_id)
        return res

    async def check_test_question(self, test_question_id: Any, user_answer: Dict[Any, str]) -> bool:
        '''Проверить ответ пользователя на вопрос'''
        res = self.check_answer(test_question_id, user_answer)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        return res

    async def check_test(self, user_answers: List[Dict[Any, str]]) -> CheckAnswerResponse:
        '''Проверить ответ пользователя на тест'''
        res = self.bulk_check_answers(user_answers)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        return res

    async def get_estimate_by_lesson(self, lesson_id: Any, user_answers: List[Dict[Any, str]]) -> int:
        '''Получить оценку за тест к уроку'''
        percentage = self.calculate_estimate(lesson_id, user_answers)
        if not percentage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test questions not found",
            )
        return percentage

    async def test_question_exists(self, test_question_id: Any) -> bool:
        '''Проверить существование теста'''
        return await self.repo.exists_by_id(test_question_id)


async def get_test_question_service(
    repo: TestQuestionRepository = Depends(get_test_question_repository),
) -> TestQuestionService:
    return TestQuestionService(repo)
