from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.repositories.review import ReviewRepository, get_review_repository
from src.repositories.course import CourseRepository, get_course_repository
from src.schemas.review_schema import ReviewCreate, ReviewUpdate
from src.services.auth_service import AuthService, get_auth_service


class ReviewService:
    def __init__(
        self,
        review_repo: ReviewRepository,
        course_repo: CourseRepository,
        auth_service: AuthService,
    ):
        self.review_repo = review_repo
        self.course_repo = course_repo
        self.auth_service = auth_service

    async def get_by_course(self, course_id: UUID):
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        return await self.review_repo.get_by_course(course_id)

    async def create(self, data: ReviewCreate):
        course = await self.course_repo.get_by_id(data.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        current_user = await self.auth_service.get_current_user()

        return await self.review_repo.create(
            user_id=current_user.uuid,
            data=data,
        )

    async def update(self, review_id: UUID, data: ReviewUpdate):
        review = await self.review_repo.get_by_id(review_id)
        if not review or review.archived:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return await self.review_repo.update(review_id, data)

    async def delete(self, review_id: UUID):
        review = await self.review_repo.get_by_id(review_id)
        if not review or review.archived:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return await self.review_repo.delete(review_id)


async def get_review_service(
    review_repo: ReviewRepository = Depends(get_review_repository),
    course_repo: CourseRepository = Depends(get_course_repository),
    auth_service: AuthService = Depends(get_auth_service),
) -> ReviewService:
    return ReviewService(review_repo, course_repo, auth_service)
