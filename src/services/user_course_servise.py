from typing import List, Dict, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.repositories.user_course import UserCourseRepository, get_user_course_repository
from src.repositories.course import CourseRepository, get_course_repository
from src.repositories.lesson import LessonRepository, get_lesson_repository
from src.repositories.test_question import TestQuestionRepository, get_test_question_repository
from src.schemas.user_course_schema import (
    UserCourseCreate,
    UserCourseProgressUpdate,
    UserCourseResponse,
    CourseWithProgressResponse,
    UserCourseDetailResponse,
    UserCourseListResponse,
    StartLessonResponse
)


class UserCourseService:
    def __init__(
        self,
        user_course_repo: UserCourseRepository,
        course_repo: CourseRepository,
        lesson_repo: LessonRepository,
        test_question_repo: TestQuestionRepository
    ):
        self.user_course_repo = user_course_repo
        self.course_repo = course_repo
        self.lesson_repo = lesson_repo
        self.test_question_repo = test_question_repo
        
    async def get_user_courses(self, user_id: UUID) -> UserCourseListResponse:
        """Получить все курсы пользователя с прогрессом"""
        user_courses = await self.user_course_repo.get_active_by_user(user_id)
        
        courses_with_progress = []
        
        for user_course in user_courses:
            # Получаем информацию о курсе
            course = await self.course_repo.get_by_id(user_course.course_id)
            if not course:
                continue
            
            if course.archived:
                continue
            # Получаем все уроки курса
            lessons = await self.lesson_repo.get_all_by_course(course.uuid)
            
            # Вычисляем прогресс
            total_lessons = len(lessons)
            #completed_lessons = len(user_course.progress) if user_course.progress else 0
            completed_lessons = await self.user_course_repo.get_completed_lessons_count(user_course.uuid)
            
            
            # Расчет общего прогресса (если есть пройденные уроки)
            overall_progress = 0
            if user_course.progress and total_lessons > 0:
                # Прогресс = количество пройденных уроков / общее количество уроков * 100
                overall_progress = (completed_lessons / total_lessons) * 100
            
            courses_with_progress.append(
                CourseWithProgressResponse(
                    course_id=course.uuid,
                    course_name=course.name,
                    course_description=course.desc,
                    total_lessons=total_lessons,
                    completed_lessons=completed_lessons,
                    overall_progress=round(overall_progress, 2),
                    user_course_id= user_course.uuid
                )
            )
        
        return UserCourseListResponse(user_courses=courses_with_progress)

    async def get_user_course_detail(
        self, 
        user_course_id: UUID, 
        user_id: UUID
    ) -> Dict[str, Any]:
    
        """Получить детальную информацию о курсе пользователя"""
        
         # Проверяем, что user_course активен
        if not await self.user_course_repo.is_user_course_active(user_course_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found or is archived"
            )
        user_course = await self.user_course_repo.get_by_id(user_course_id)
        
        if not user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found"
            )
        
        # Проверяем, что курс принадлежит пользователю
        if user_course.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this course"
            )
        
        course = await self.course_repo.get_by_id(user_course.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        if course.archived:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot access archived course"
            )
        
        # Получаем все уроки курса
        lessons = await self.lesson_repo.get_all_by_course(course.uuid, skip=0, limit=1000)
        
        # Формируем прогресс по урокам
        progress_for_lessons = []
        
        for lesson in lessons:
            
            if lesson.archived:
                continue
            
            lesson_progress = await self.user_course_repo.get_lesson_progress(
                user_course_id,
                lesson.uuid
            )
            
            # Проверяем, пройден ли урок
            completed = await self.user_course_repo.is_lesson_completed(
                user_course_id,
                lesson.uuid
            )
            
            lesson_data = {
                "lesson_id": lesson.uuid,
                "lesson_name": lesson.name,
                "started": lesson_progress is not None,
                "completed": completed
            }
            
            # Если есть прогресс, добавляем детали
            if lesson_progress:
                lesson_data["questions"] = lesson_progress.get("questions", [])
                
                # Если урок пройден, добавляем среднюю оценку
                if completed:
                    avg_estimate = await self.user_course_repo.get_lesson_average_estimate(
                        user_course_id,
                        lesson.uuid
                    )
                    if avg_estimate is not None:
                        lesson_data["estimate"] = round(avg_estimate, 2)
            
            progress_for_lessons.append(lesson_data)
        
        return {
            "user_id": user_id,
            "course_id": course.uuid,
            "course_name": course.name,
            "progress_for_lessons": progress_for_lessons
        }

    async def enroll_in_course(self, user_id: UUID, course_id: UUID) -> UserCourseResponse:
        """Записать пользователя на курс"""
        # Проверяем существование курса
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Проверяем, что курс активен
        if course.archived:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot enroll in archived course"
            )
        
        # Ищем активный user_course
        existing_active = await self.user_course_repo.get_active_by_user_and_course(user_id, course_id)
        if existing_active:
            return UserCourseResponse.model_validate(existing_active)
        
        # Ищем архивированный user_course
        existing_archived = await self.user_course_repo.get_by_user_and_course(user_id, course_id)
        if existing_archived and existing_archived.archived:
            # Активируем архивированный курс
            existing_archived.archived = False
            await self.user_course_repo.db.commit()
            await self.user_course_repo.db.refresh(existing_archived)
            return UserCourseResponse.model_validate(existing_archived)
        
        # Создаем новую запись о курсе пользователя
        user_course_data = {
            "user_id": user_id,
            "course_id": course_id,
            "progress": []
        }
        
        user_course = await self.user_course_repo.create(user_course_data)
        return UserCourseResponse.model_validate(user_course)
        
    
    async def update_question_progress(
        self,
        user_course_id: UUID,
        lesson_id: UUID,
        question_id: UUID,
        estimate: float
    ) -> UserCourseResponse:
        """Обновить оценку для конкретного вопроса в уроке"""
        
        # Проверяем, что user_course активен
        if not await self.user_course_repo.is_user_course_active(user_course_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found or is archived"
            )
        
        user_course = await self.user_course_repo.get_by_id(user_course_id)
        if not user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found"
            )
        
        # Проверяем, что оценка 0 или 100
        if estimate not in (0, 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estimate must be 0 or 100"
            )
        # Проверяем, что вопрос активен
        if not await self.test_question_repo.is_question_active(question_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update progress for archived question"
            )
            
        # Получаем текущий прогресс по уроку
        lesson_progress = await self.user_course_repo.get_lesson_progress(
            user_course_id,
            lesson_id
        )
        
        if not lesson_progress:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lesson not started yet or not found in progress"
            )
        
        # Проверяем, существует ли вопрос в прогрессе
        existing_questions = lesson_progress.get("questions", [])
        question_found = False
        
        for question in existing_questions:
            if isinstance(question, dict):
                q_id = question.get("question_id")
                if isinstance(q_id, str):
                    q_uuid = UUID(q_id)
                elif isinstance(q_id, UUID):
                    q_uuid = q_id
                else:
                    continue
                
                if q_uuid == question_id:
                    question_found = True
                    break
        
        if not question_found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question not found in lesson progress"
            )
        
        # Обновляем оценку для вопроса
        update_data = [{
            "question_id": question_id,
            "estimate": estimate
        }]
        
        updated_user_course = await self.user_course_repo.update_progress(
            user_course_id,
            lesson_id,
            update_data
        )
        
        if not updated_user_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update question progress"
            )
        
        return UserCourseResponse.model_validate(updated_user_course)

    async def get_lesson_progress(
        self,
        user_id: UUID,
        lesson_id: UUID
    ) -> Dict[str, Any]:
        """Получить прогресс пользователя по конкретному уроку"""
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
            
        if lesson.archived:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot access archived lesson"
            )
        
        # Находим курс пользователя
        user_course = await self.user_course_repo.get_by_user_and_course(
            user_id,
            lesson.course_id
        )
        
        if not user_course:
            return {
                "lesson_id": lesson_id,
                "lesson_name": lesson.name,
                "started": False,
                "completed": False,
                "message": "Lesson not started"
            }
        
        # Получаем прогресс по уроку
        lesson_progress = await self.user_course_repo.get_lesson_progress(
            user_course.uuid,
            lesson_id
        )
        
        # Проверяем, начат ли урок
        started = lesson_progress is not None
        
        # Проверяем, пройден ли урок
        completed = await self.user_course_repo.is_lesson_completed(
            user_course.uuid,
            lesson_id
        )
        
        response = {
            "lesson_id": lesson_id,
            "lesson_name": lesson.name,
            "started": started,
            "completed": completed
        }
        
        # Если урок пройден, добавляем среднюю оценку
        if completed and lesson_progress:
            avg_estimate = await self.user_course_repo.get_lesson_average_estimate(
                user_course.uuid,
                lesson_id
            )
            if avg_estimate is not None:
                response["estimate"] = round(avg_estimate, 2)
        
        return response
    
    async def soft_delete_user_course(
        self,
        user_course_id: UUID,
        current_user_id: UUID
    ) -> UserCourseResponse:
        """Мягкое удаление user_course (только для админов)"""
        
        # Проверяем, что user_course существует и активен
        if not await self.user_course_repo.is_user_course_active(user_course_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found or already archived"
            )
            
        user_course = await self.user_course_repo.get_by_id(user_course_id)
        if not user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found"
            )
        
        soft_deleted_user_course = await self.user_course_repo.delete(user_course_id)
        
        if not soft_deleted_user_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to soft delete user course"
            )
        
        return UserCourseResponse.model_validate(soft_deleted_user_course)
    
    
    async def reset_user_course_progress(
        self,
        user_course_id: UUID,
    ) -> UserCourseResponse:
        """Сбросить прогресс пользователя по курсу"""
        # Проверяем, что user_course существует и активен
        if not await self.user_course_repo.is_user_course_active(user_course_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found or is archived"
            )
        
        user_course = await self.user_course_repo.get_by_id(user_course_id)
        if not user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User course not found"
            )
        
        # Сбрасываем прогресс
        reset_user_course = await self.user_course_repo.reset_progress(user_course_id)
        
        if not reset_user_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset user course progress"
            )
        
        return UserCourseResponse.model_validate(reset_user_course)
    
    
async def get_user_course_service(
    user_course_repo: UserCourseRepository = Depends(get_user_course_repository),
    course_repo: CourseRepository = Depends(get_course_repository),
    lesson_repo: LessonRepository = Depends(get_lesson_repository),
    test_question_repo: TestQuestionRepository = Depends(get_test_question_repository),
):
    return UserCourseService(user_course_repo, course_repo, lesson_repo, test_question_repo)