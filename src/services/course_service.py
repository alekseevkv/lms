from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.repositories.course import CourseRepository, get_course_repository
from src.schemas.course_schema import CourseResponse


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


async def get_course_service(
    repo: CourseRepository = Depends(get_course_repository),
) -> CourseService:
    return CourseService(repo)
