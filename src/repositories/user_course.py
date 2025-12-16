from collections.abc import Sequence
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.user_course import UserCourse
from src.models.test_question import TestQuestion
from src.models.course import Course
from src.models.lesson import Lesson
from src.models.user import User


class UserCourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_user_course_active(self, user_course_id: UUID) -> bool:
        """Проверяет, активен ли user_course (не архивирован)"""
        result = await self.db.execute(
            select(UserCourse).where(UserCourse.uuid == user_course_id, UserCourse.archived == False)
        )
        return result.scalar_one_or_none() is not None
    
    
    async def get_by_id(self, user_course_id: UUID) -> Optional[UserCourse]: #UserCourse | None:
        result = await self.db.execute(
            select(UserCourse).where(
                UserCourse.uuid == user_course_id,
                UserCourse.archived == False
            )
        )
        return result.scalar_one_or_none()
    async def get_active_by_user(self, user_id: UUID) -> List[UserCourse]:
        """Получить активные курсы пользователя (не архивированные)"""
        result = await self.db.execute(
            select(UserCourse)
            .where(UserCourse.user_id == user_id, UserCourse.archived == False)
        )
        return list(result.scalars().all())
    
    async def get_by_user_and_course(self, user_id: UUID, course_id: UUID) -> Optional[UserCourse]:  #UserCourse | None:
        result = await self.db.execute(
            select(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.course_id == course_id,
            )
        )
        return result.scalar_one_or_none()
    async def get_active_by_user_and_course(self, user_id: UUID, course_id: UUID) -> Optional[UserCourse]:
        """Получить активный user_course по пользователю и курсу (не архивированный)"""
        result = await self.db.execute(
            select(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.course_id == course_id,
                UserCourse.archived == False
            )
        )
        return result.scalar_one_or_none()
    async def get_all_by_user(
        self, user_id: UUID
        )-> List[UserCourse]:
        result = await self.db.execute(
            select(UserCourse)
            .where(UserCourse.user_id == user_id,
                )
        )
        return list(result.scalars().all())

    async def create(self, user_course_data: Dict[str, Any]) -> UserCourse:
        user_course = UserCourse(**user_course_data)
        self.db.add(user_course)
        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course

    
    async def update(self, user_course_id: UUID, update_data: Dict[str, Any]) -> Optional[UserCourse]:
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None

        for key, value in update_data.items():
            setattr(user_course, key, value)

        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course
    
    async def update_progress(
        self,
        user_course_id: UUID,
        lesson_id: UUID,
        question_progress: List[Dict[str, Any]]
    ) -> Optional[UserCourse]:
        """Обновить прогресс по уроку с детализацией по вопросам"""
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None
        
        lesson_id_str = str(lesson_id)
        
        # Инициализируем прогресс как список словарей
        current_progress: List[Dict[str, Any]]
        
        if user_course.progress is None:
            current_progress = []
        elif isinstance(user_course.progress, list):
            # Создаем глубокую копию прогресса
            current_progress = []
            for item in user_course.progress:
                if isinstance(item, dict):
                    item_copy = dict(item)
                    # Нормализуем lesson_id если есть
                    if "lesson_id" in item_copy and isinstance(item_copy["lesson_id"], UUID):
                        item_copy["lesson_id"] = str(item_copy["lesson_id"])
                    # Нормализуем вопросы если есть
                    if "questions" in item_copy and isinstance(item_copy["questions"], list):
                        questions_copy = []
                        for q in item_copy["questions"]:
                            if isinstance(q, dict):
                                q_copy = dict(q)
                                if "question_id" in q_copy and isinstance(q_copy["question_id"], UUID):
                                    q_copy["question_id"] = str(q_copy["question_id"])
                                questions_copy.append(q_copy)
                        item_copy["questions"] = questions_copy
                    current_progress.append(item_copy)
        else:
            # Если это не список, начинаем заново
            current_progress = []
        
        # Находим урок в прогрессе
        lesson_index = -1
        for i, lesson_item in enumerate(current_progress):
            if isinstance(lesson_item, dict):
                item_lesson_id = lesson_item.get("lesson_id")
                # Нормализуем lesson_id для сравнения
                if isinstance(item_lesson_id, UUID):
                    item_lesson_id = str(item_lesson_id)
                elif item_lesson_id is not None:
                    item_lesson_id = str(item_lesson_id)
                
                if item_lesson_id == lesson_id_str:
                    lesson_index = i
                    break
        
        if lesson_index == -1:
            # Если урок не найден, создаем новый
            new_lesson_progress = {
                "lesson_id": lesson_id_str,
                "questions": [
                    {
                        "question_id": str(qp.get("question_id")),
                        "estimate": qp.get("estimate", 0)
                    }
                    for qp in question_progress
                    if qp.get("question_id") and qp.get("estimate") is not None
                ]
            }
            current_progress.append(new_lesson_progress)
        else:
            # Обновляем существующий урок
            existing_questions = current_progress[lesson_index].get("questions", [])
            if not isinstance(existing_questions, list):
                existing_questions = []
            
            # Создаем словарь для быстрого доступа к существующим вопросам
            questions_dict = {}
            for q in existing_questions:
                if isinstance(q, dict):
                    q_id = q.get("question_id")
                    if q_id:
                        q_id_str = str(q_id)
                        questions_dict[q_id_str] = {
                            "question_id": q_id_str,
                            "estimate": q.get("estimate", 0)
                        }
            
            # Обновляем оценки для указанных вопросов
            for qp in question_progress:
                if isinstance(qp, dict):
                    q_id = qp.get("question_id")
                    estimate = qp.get("estimate")
                    
                    if q_id and estimate is not None:
                        q_id_str = str(q_id)
                        
                        # Если вопрос уже существует в прогрессе, обновляем оценку
                        if q_id_str in questions_dict:
                            questions_dict[q_id_str]["estimate"] = estimate
                        else:
                            # Если вопрос не существует, добавляем его (хотя это не должно происходить)
                            questions_dict[q_id_str] = {
                                "question_id": q_id_str,
                                "estimate": estimate
                            }
                            print(f"Warning: Question {q_id_str} was not found in existing progress, adding it")
            
            # Обновляем список вопросов
            current_progress[lesson_index]["questions"] = list(questions_dict.values())
        
        # Присваиваем обновленный прогресс
        user_course.progress = current_progress  # type: ignore
        
        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course

    #обновлен
    async def get_lesson_progress(
        self,
        user_course_id: UUID,
        lesson_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Получить прогресс по конкретному уроку"""
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None
        
        lesson_id_str = str(lesson_id)
        
        for lesson_progress in user_course.progress or []:
            if isinstance(lesson_progress, dict) and str(lesson_progress.get("lesson_id")) == lesson_id_str:
                return lesson_progress
        
        return None
    
    #обновлен
    async def get_course_with_lessons_and_progress(self, user_course_id: UUID) -> Optional[Dict[str, Any]]:
        """Получить курс с уроками и прогрессом пользователя"""
        # Сначала получаем user_course
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None
        
        # Затем получаем курс
        course_result = await self.db.execute(
            select(Course).where(Course.uuid == user_course.course_id)
        )
        course = course_result.scalar_one_or_none()
        
        if not course:
            return None
        
        # Получаем все уроки курса
        lessons_result = await self.db.execute(
            select(Lesson).where(Lesson.course_id == course.uuid)
        )
        lessons = lessons_result.scalars().all()
        
        # Структурируем данные
        course_data = {
            "course": course.to_dict(),
            "user_course": user_course.to_dict()
        }
        
        lessons_with_progress = []
        
        for lesson in lessons:
            # Находим оценку для этого урока в прогрессе пользователя
            lesson_progress = None
            lesson_id_str = str(lesson.uuid)
            
            if user_course.progress:
                for progress_item in user_course.progress:
                    if isinstance(progress_item, dict) and str(progress_item.get("lesson_id")) == lesson_id_str:
                        lesson_progress = progress_item
                        break
                    
            lessons_with_progress.append({
                "lesson": lesson.to_dict(),
                "progress": lesson_progress
            })
        
        return {
            **course_data,
            "lessons_with_progress": lessons_with_progress
        }
        
        
    async def delete(self, user_course_id: UUID) -> Optional[UserCourse]:
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None
    
        user_course.archived = True
        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course
    
    async def get_completed_lessons_count(self, user_course_id: UUID) -> int:
        """Получить количество пройденных уроков в курсе"""
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return 0

        completed_count = 0
        if not user_course.progress:
            return 0

        # Для каждого урока в прогрессе проверяем, пройден ли он
        for lesson_progress in user_course.progress:
            if not isinstance(lesson_progress, dict):
                continue

            lesson_id = lesson_progress.get("lesson_id")
            if not lesson_id:
                continue

            # Получаем количество вопросов в тесте для урока
            questions_count_result = await self.db.execute(
                select(func.count(TestQuestion.uuid))
                .where(
                    TestQuestion.lesson_id == UUID(lesson_id),
                    TestQuestion.archived == False
                )
            )
            total_questions = questions_count_result.scalar() or 0

            # Получаем количество отвеченных вопросов
            answered_questions = lesson_progress.get("questions", [])
            answered_count = len(answered_questions) if isinstance(answered_questions, list) else 0

            # Урок считается пройденным, если ответы даны на все вопросы
            if total_questions > 0 and answered_count >= total_questions:
                completed_count += 1

        return completed_count

    async def is_lesson_completed(self, user_course_id: UUID, lesson_id: UUID) -> bool:
        """Проверить, пройден ли конкретный урок"""
        user_course = await self.get_by_id(user_course_id)
        if not user_course or not user_course.progress:
            return False

        lesson_id_str = str(lesson_id)
        
        # Находим прогресс по уроку
        lesson_progress = None
        for progress_item in user_course.progress:
            if isinstance(progress_item, dict) and str(progress_item.get("lesson_id")) == lesson_id_str:
                lesson_progress = progress_item
                break

        if not lesson_progress:
            return False

        # Получаем количество вопросов в тесте для урока
        questions_count_result = await self.db.execute(
            select(func.count(TestQuestion.uuid))
            .where(
                TestQuestion.lesson_id == lesson_id,
                TestQuestion.archived == False
            )
        )
        total_questions = questions_count_result.scalar() or 0

        # Получаем количество отвеченных вопросов
        answered_questions = lesson_progress.get("questions", [])
        answered_count = len(answered_questions) if isinstance(answered_questions, list) else 0

        # Урок считается пройденным, если ответы даны на все вопросы
        return total_questions > 0 and answered_count >= total_questions

    async def get_lesson_average_estimate(self, user_course_id: UUID, lesson_id: UUID) -> Optional[float]:
        """Получить среднюю оценку за урок"""
        user_course = await self.get_by_id(user_course_id)
        if not user_course or not user_course.progress:
            return None

        lesson_id_str = str(lesson_id)
        
        # Находим прогресс по уроку
        lesson_progress = None
        for progress_item in user_course.progress:
            if isinstance(progress_item, dict) and str(progress_item.get("lesson_id")) == lesson_id_str:
                lesson_progress = progress_item
                break

        if not lesson_progress:
            return None

        answered_questions = lesson_progress.get("questions", [])
        if not isinstance(answered_questions, list) or not answered_questions:
            return 0.0

        # Вычисляем среднюю оценку
        total_estimate = sum(q.get("estimate", 0) for q in answered_questions if isinstance(q, dict))
        return total_estimate / len(answered_questions)
    
    async def reset_progress(self, user_course_id: UUID) -> Optional[UserCourse]:
        """Сбросить прогресс пользователя по курсу (очищает поле progress)"""
        user_course = await self.get_by_id(user_course_id)
        if not user_course:
            return None
        
        if user_course.archived:
            return None
    
        # Сбрасываем прогресс на пустой список
        user_course.progress = []  # type: ignore
        
        await self.db.commit()
        await self.db.refresh(user_course)
        return user_course
    
async def get_user_course_repository(
    db: AsyncSession = Depends(get_session),
) -> UserCourseRepository:
    return UserCourseRepository(db)