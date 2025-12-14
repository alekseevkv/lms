from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.schemas.review_schema import ReviewCreate, ReviewResponse, ReviewUpdate
from src.services.review_service import ReviewService, get_review_service

router = APIRouter()

@router.get(
    "/{course_id}",
    response_model=list[ReviewResponse],
    summary="Get reviews for course",
)
async def get_reviews_for_course(
    course_id: UUID,
    service: Annotated[ReviewService, Depends(get_review_service)],
):
    return await service.get_by_course(course_id)


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create review",
)
async def create_review(
    data: ReviewCreate,
    service: Annotated[ReviewService, Depends(get_review_service)],
):
    return await service.create(data)


@router.patch(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Update or delete review",
)
async def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    service: Annotated[ReviewService, Depends(get_review_service)],
    delete: bool = Query(False, description="If true, review will be archived"),
):
    if delete:
        return await service.delete(review_id)
    return await service.update(review_id, data)
