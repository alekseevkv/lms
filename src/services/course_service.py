from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.repositories.course import CourseRepository, get_course_repository
from src.schemas.course_schema import (
    CourseResponse,
    CourseBase,
    CourseUpdate
)


class CourseService:
    def __init__(self, repo):
        self.repo = repo

    async def get_all(
        self, skip: int | None, limit: int | None
    ) -> list[CourseResponse]:
        res = await self.repo.get_all(skip=skip, limit=limit)

        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Courses not found",
            )

        return res

    async def get_by_id(self, id: UUID) -> CourseResponse:
        res = await self.repo.get_by_id(id)

        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        return res

    async def create_course(self, course_date: CourseBase) -> CourseResponse:
        if await self.check_name(course_date.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A course with this name already exists",
            )
        res = await self.repo.create(course_date.model_dump())
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course creation failed",
            )
        return res

    async def update_course(self, id:UUID, update_date: CourseUpdate) -> CourseResponse:
        course = await self.get_by_id(id)

        if update_date.name and update_date.name != course.name:
            if await self.check_name(update_date.name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A course with this name already exists",
                )

        update_dict = {k: v for k, v in update_date.model_dump().items() if v is not None}

        if update_dict:
            res = await self.repo.update(id, update_dict)
            return res

        return course

    async def check_name(self, name: str) -> CourseResponse | None:
        return await self.repo.exists_by_name(name)

    async def delete_course(self, id:UUID):
        res = await self.repo.delete(id)

        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course not found",
            )


async def get_course_service(
    repo: CourseRepository = Depends(get_course_repository),
) -> CourseService:
    return CourseService(repo)
