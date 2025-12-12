from typing import List, Dict, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.repositories.user_course import UserCourseRepository, get_user_course_repository
from src.repositories.course import CourseRepository, get_course_repository
from src.repositories.lesson import LessonRepository, get_lesson_repository
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
        lesson_repo: LessonRepository
    ):
        self.user_course_repo = user_course_repo
        self.course_repo = course_repo
        self.lesson_repo = lesson_repo

    async def get_user_courses(self, user_id: UUID) -> UserCourseListResponse:
        """Получить все курсы пользователя с прогрессом"""
        user_courses = await self.user_course_repo.get_all_by_user(user_id)
        
        courses_with_progress = []
        
        for user_course in user_courses:
            # Получаем информацию о курсе
            course = await self.course_repo.get_by_id(user_course.course_id)
            if not course:
                continue
            
            # Получаем все уроки курса
            lessons = await self.lesson_repo.get_all_by_course(course.uuid)
            
            # Вычисляем прогресс
            total_lessons = len(lessons)
            completed_lessons = len(user_course.progress) if user_course.progress else 0
            
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
                    overall_progress=round(overall_progress, 2)
                )
            )
        
        return UserCourseListResponse(user_courses=courses_with_progress)

    async def get_user_course_detail(
        self, 
        user_course_id: UUID, 
        user_id: UUID
    ) -> UserCourseDetailResponse:
        """Получить детальную информацию о курсе пользователя"""
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
        
        # Получаем детальную информацию о курсе с уроками и прогрессом
        course_detail = await self.user_course_repo.get_course_with_lessons_and_progress(
            user_course_id
        )
        
        if not course_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        return UserCourseDetailResponse(**course_detail)

    async def enroll_in_course(self, user_id: UUID, course_id: UUID) -> UserCourseResponse:
        """Записать пользователя на курс"""
        # Проверяем, не записан ли уже пользователь на курс
        existing = await self.user_course_repo.get_by_user_and_course(user_id, course_id)
        if existing:
            return UserCourseResponse.model_validate(existing)
        
        # Проверяем существование курса
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Создаем запись о курсе пользователя
        user_course_data = {
            "user_id": user_id,
            "course_id": course_id,
            "progress": []  # Начинаем с пустого прогресса
        }
        
        user_course = await self.user_course_repo.create(user_course_data)
        return UserCourseResponse.model_validate(user_course)

    async def update_lesson_progress(
        self, 
        user_course_id: UUID, 
        user_id: UUID,
        progress_update: UserCourseProgressUpdate
    ) -> UserCourseResponse:
        """Обновить прогресс по уроку"""
        # Получаем курс пользователя
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
                detail="You don't have permission to update this course"
            )
        
        # Проверяем существование урока
        lesson = await self.lesson_repo.get_by_id(progress_update.lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Проверяем, что урок принадлежит курсу
        if lesson.course_id != user_course.course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lesson does not belong to this course"
            )
        
        # Обновляем прогресс
        updated_user_course = await self.user_course_repo.update_progress(
            user_course_id,
            progress_update.lesson_id,
            progress_update.estimate
        )
        
        if not updated_user_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to update progress"
            )
        
        return UserCourseResponse.model_validate(updated_user_course)

    async def start_lesson(self, user_id: UUID, lesson_id: UUID) -> StartLessonResponse:
        """Начать прохождение урока"""
        # Получаем информацию об уроке
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Находим курс пользователя для этого урока
        user_course = await self.user_course_repo.get_by_user_and_course(
            user_id, 
            lesson.course_id
        )
        
        if not user_course:
            # Если пользователь не записан на курс, записываем его
            await self.enroll_in_course(user_id, lesson.course_id)
        
        # Проверяем, не начат ли уже урок
        if user_course and user_course.progress:
            for progress_item in user_course.progress:
                if progress_item.get("lesson_id") == str(lesson_id):
                    # Урок уже начат, возвращаем информацию
                    return StartLessonResponse(
                        lesson_id=lesson_id,
                        lesson_name=lesson.name,
                        message="Lesson already started"
                    )
        
        return StartLessonResponse(
            lesson_id=lesson_id,
            lesson_name=lesson.name,
            message="Lesson started successfully. You can now proceed with the test."
        )

    async def get_lesson_progress(
        self, 
        user_id: UUID, 
        lesson_id: UUID
    ) -> Dict[str, Any]:
        """Получить прогресс пользователя по конкретному уроку"""
        # Получаем информацию об уроке
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Находим курс пользователя
        user_course = await self.user_course_repo.get_by_user_and_course(
            user_id, 
            lesson.course_id
        )
        
        if not user_course:
            return {
                "lesson_id": lesson_id,
                "started": False,
                "estimate": None,
                "message": "Lesson not started yet"
            }
        
        # Ищем прогресс по этому уроку
        lesson_progress = None
        if user_course.progress:
            for progress_item in user_course.progress:
                if progress_item.get("lesson_id") == str(lesson_id):
                    lesson_progress = progress_item
                    break
        
        if lesson_progress:
            return {
                "lesson_id": lesson_id,
                "started": True,
                "estimate": lesson_progress.get("estimate"),
                "completed": lesson_progress.get("estimate", 0) > 0  # Считаем пройденным если есть оценка
            }
        else:
            return {
                "lesson_id": lesson_id,
                "started": False,
                "estimate": None,
                "message": "Lesson not started yet"
            }


async def get_user_course_service(
    user_course_repo: UserCourseRepository = Depends(get_user_course_repository),
    course_repo: CourseRepository = Depends(get_course_repository),
    lesson_repo: LessonRepository = Depends(get_lesson_repository),
):
    return UserCourseService(user_course_repo, course_repo, lesson_repo)