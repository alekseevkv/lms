from typing import Any, List, Dict, Sequence

from fastapi import Depends
from sqlalchemy import select, func, not_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.test_question import TestQuestion


class TestQuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, question_id: Any) -> TestQuestion | None:
        '''Получить тест по ID'''
        result = await self.db.execute(select(TestQuestion).where(TestQuestion.uuid == question_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[TestQuestion]:
        '''Получить все тесты'''
        result = await self.db.execute(select(TestQuestion).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_lesson_id(self, lesson_id: str) -> Sequence[TestQuestion] | None:
        '''Получить тесты по ID урока'''
        result = await self.db.execute(
            select(TestQuestion)
            .where(
                TestQuestion.lesson_id == lesson_id,
                not_(TestQuestion.archived))
                .order_by(TestQuestion.question_num))
        return result.scalars().all()

    async def get_count(self) -> int | None:
        '''Получить общее количество тестов'''
        result = await self.db.execute(select(func.count(TestQuestion.uuid)).where(
            not_(TestQuestion.archived))
        )
        return result.scalar()

    async def get_count_by_lesson(self, lesson_id: Any) -> int | None:
        '''Получить количество тестов в уроке'''
        result = await self.db.execute(
            select(func.count(TestQuestion.uuid)).where(
                TestQuestion.lesson_id == lesson_id, not_(TestQuestion.archived))
        )
        return result.scalar()

    async def create(self, test_question_data: Dict[str, Any]) -> TestQuestion:
        '''Создать новый тест'''
        test_question = TestQuestion(**test_question_data)
        self.db.add(test_question)
        await self.db.commit()
        await self.db.refresh(test_question)
        return test_question

    async def create_many(self, test_questions_data: List[Dict[str, Any]]) -> List[TestQuestion]:
        '''Создать несколько тестов'''
        test_questions = []
        for data in test_questions_data:
            teast_question = TestQuestion(**data)
            test_questions.append(teast_question)
            self.db.add(teast_question)
        await self.db.commit()

        for teast_question in test_questions:
            await self.db.refresh(teast_question)

        return test_questions

    async def update(self, test_question_id: Any, test_question_data: Dict[str, Any]) -> TestQuestion | None:
        '''Обновить тест'''
        test_question = await self.get_by_id(test_question_id)
        if test_question:
            for key, value in test_question_data.items():
                setattr(test_question, key, value)
            await self.db.commit()
            await self.db.refresh(test_question)
        return test_question

    async def delete(self, test_question_id: Any) -> TestQuestion | None:
        '''Удалить тест'''
        test_question = await self.get_by_id(test_question_id)
        if test_question:
            test_question.archived = True
            await self.db.commit()
            await self.db.refresh(test_question)
        return test_question

    async def get_correct_answer(self, question_id: Any) -> str | None:
        '''Получить правильный ответ по ID'''
        result = await self.db.execute(
            select(TestQuestion.correct_answer).where(
                TestQuestion.uuid == question_id)
        )
        question = result.first()
        return question[0] if question else None

    async def check_answer(self, question_id: Any, user_answer: str) -> bool:
        '''Проверить ответ пользователя на вопрос'''
        correct_answer = await self.get_correct_answer(question_id)
        return correct_answer is not None and user_answer.strip().lower() == correct_answer.strip().lower()

    async def bulk_check_answers(self, answers_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        '''Проверить ответ пользователя на тест'''
        results = []

        for answer_data in answers_data:
            passed = await self.check_answer(answer_data["uuid"], answer_data["user_answer"])
            correct_answer = await self.get_correct_answer(answer_data["uuid"])

            results.append({
                "uuid": answer_data["uuid"],
                "passed": passed,
                "correct_answer": correct_answer or ""
            })

        return results

    async def calculate_estimate(self, lesson_id: int, user_answers: List[Dict[str, Any]]) -> float:
        '''Рассчитать оценку (%) для урока'''
        total_questions = await self.get_count_by_lesson(lesson_id)
        if total_questions is None:
            return 0

        total_correct = 0
        results = await self.bulk_check_answers(user_answers)
        for result in results:
            if result["passed"]:
                total_correct += 1

        percentage = (total_correct / total_questions) * 100
        return percentage

    async def exists_by_id(self, test_question_id: Any) -> bool:
        test_question = await self.get_by_id(test_question_id)
        return test_question is not None


async def get_test_question_repository(
    db: AsyncSession = Depends(get_session),
) -> TestQuestionRepository:
    return TestQuestionRepository(db)
