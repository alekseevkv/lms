from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.repositories.lesson import LessonRepository, get_lesson_repository
from src.schemas.lesson_schema import (
    LessonResponse,
    LessonCreate,
    LessonUpdate,
    LessonVideoResponse
)


class LessonService:
    def __init__(self, repo: LessonRepository):
        self.repo = repo

    async def get_by_id(
        self, 
        lesson_id: UUID, 
        video_only: bool = False
    ) -> LessonResponse | LessonVideoResponse:
        lesson = await self.repo.get_by_id(lesson_id)
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

        if video_only:
            return LessonVideoResponse.model_validate(lesson)
            
        return LessonResponse.model_validate(lesson)

    async def get_all_by_course(
        self, 
        course_id: UUID, 
        skip: int | None = 0, 
        limit: int | None = 100
    ) -> list[LessonResponse]:
        lessons = await self.repo.get_all_by_course(
            course_id, 
            skip=skip, 
            limit=limit
        )
        
        if not lessons:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No lessons found for this course",
            )
        
        return [LessonResponse.model_validate(lesson) for lesson in lessons]
        
    async def create_lesson(self, lesson_data: LessonCreate) -> LessonResponse:
        # Проверяем, существует ли урок с таким именем в курсе
        if await self.repo.exists_by_name_in_course(
            lesson_data.name, 
            lesson_data.course_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A lesson with this name already exists in this course",
            )
            
        from src.repositories.course import CourseRepository
        course_repo = CourseRepository(self.repo.db)
        if not await course_repo.is_course_active(lesson_data.course_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create lesson for archived course",
            )
            
        lesson_dict = lesson_data.model_dump()
        if lesson_dict.get('video_url'):
            lesson_dict['video_url'] = str(lesson_dict['video_url'])
        
        lesson = await self.repo.create(lesson_dict)
        return LessonResponse.model_validate(lesson)
    
    
    async def update_lesson(
        self, 
        lesson_id: UUID, 
        update_data: LessonUpdate
    ) -> LessonResponse:
        lesson = await self.repo.get_by_id(lesson_id)
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Преобразуем HttpUrl в строку если есть video_url
        if 'video_url' in update_dict and update_dict['video_url']:
            update_dict['video_url'] = str(update_dict['video_url'])
        
        # Проверяем уникальность имени если оно обновляется
        if 'name' in update_dict and update_dict['name'] != lesson.name:
            if await self.repo.exists_by_name_in_course(
                update_dict['name'], 
                lesson.course_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A lesson with this name already exists in this course",
                )
        
        updated_lesson = await self.repo.update(lesson_id, update_dict)
        

        if not updated_lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found after update",
            )
        return LessonResponse.model_validate(updated_lesson)

    async def delete_lesson(self, lesson_id: UUID) -> None:
        lesson = await self.repo.delete(lesson_id)
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )


async def get_lesson_service(
    repo: LessonRepository = Depends(get_lesson_repository),
) -> LessonService:
    return LessonService(repo)