from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.review import ReviewRepository
from src.schemas.review_schema import ReviewCreate, ReviewResponse, ReviewUpdate
from src.services.database import get_session


router = APIRouter()


async def get_review_repo(
    session: AsyncSession = Depends(get_session),
) -> ReviewRepository:
    return ReviewRepository(session)


@router.get(
    "/{course_id}",
    response_model=list[ReviewResponse],
    summary="Get reviews for course",
)
async def get_reviews_for_course(
    course_id: int,
    repo: Annotated[ReviewRepository, Depends(get_review_repo)],
):
    reviews = await repo.get_by_course(course_id)
    return reviews


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create review",
)
async def create_review(
    data: ReviewCreate,
    repo: Annotated[ReviewRepository, Depends(get_review_repo)],
):
    review = await repo.create(data)
    return review


@router.patch(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Update or delete review",
)
async def update_review(
    review_id: int,
    data: ReviewUpdate,
    repo: Annotated[ReviewRepository, Depends(get_review_repo)],
    delete: bool = False,
):
    review = await repo.get_by_id(review_id)
    if review is None or review.archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    if delete:
        review = await repo.delete(review_id)
    else:
        review = await repo.update(review_id, data)

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return review
