from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Review
from src.schemas.review_schema import ReviewCreate, ReviewUpdate


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, review_uuid: Any) -> Review | None:
        result = await self.db.execute(
            select(Review).where(Review.uuid == review_uuid)
        )
        return result.scalar_one_or_none()

    async def get_by_course(
        self,
        course_id: Any,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Review]:
        result = await self.db.execute(
            select(Review)
            .where(Review.course_id == course_id, Review.archived.is_(False))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, user_id: UUID, data: ReviewCreate) -> Review:
        review = Review(
            user_id=user_id,
            course_id=data.course_id,
            content=data.content,
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def update(self, review_uuid: Any, data: ReviewUpdate) -> Review | None:
        review = await self.get_by_id(review_uuid)
        if not review:
            return None

        if data.content is not None:
            review.content = data.content

        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review_uuid: Any) -> Review | None:
        review = await self.get_by_id(review_uuid)
        if not review:
            return None

        review.archived = True
        await self.db.commit()
        await self.db.refresh(review)
        return review
