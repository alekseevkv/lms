from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.schemas.course_schema import CourseBase, CourseResponse, CourseUpdate
from src.schemas.user_schema import (
    DeleteUserByAdminResponse,
    UpdateUserByAdminRequest,
    UserResponse,
    UserResponseWithId,
    UserRole,
)
from src.services.auth_service import AuthService, get_auth_service
from src.services.course_service import CourseService, get_course_service
from src.services.user_service import UserService, get_user_service

router = APIRouter()


@router.post("/course", response_model=CourseResponse, summary="Create a new course")
async def add_course(
    course_date: CourseBase,
    service: CourseService = Depends(get_course_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User can only be updated by admin",
        )

    res = await service.create_course(course_date)

    return res


@router.patch(
    "/course/{course_id}/update",
    response_model=CourseResponse,
    summary="Update a course by id",
)
async def update_course(
    course_id: UUID,
    course_date: CourseUpdate,
    service: CourseService = Depends(get_course_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User can only be updated by admin",
        )
    res = await service.update_course(course_id, course_date)

    return res


@router.patch("/course/{course_id}/delete", summary="Delete a course by id")
async def delete_course(
    course_id: UUID,
    service: CourseService = Depends(get_course_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User can only be updated by admin",
        )

    await service.delete_course(course_id)
    return {"message": "Course delete successfully"}


@router.patch("/users", response_model=UserResponse, summary="Update user by admin")
async def update_user_by_admin(
    data: UpdateUserByAdminRequest,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User can only be updated by admin",
        )

    updated_user = await user_service.update_user_by_admin(data)

    return updated_user


@router.delete(
    "/users/{user_id}/",
    response_model=DeleteUserByAdminResponse,
    summary="Delete user by admin",
)
async def delete_user_by_admin(
    user_id: UUID,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User can only be deleted by admin",
        )

    await user_service.delete_user_by_admin(user_id)

    return {"msg": "User has been successfully deleted"}


@router.get(
    "/users/",
    response_model=list[UserResponseWithId],
    summary="Get active users by admin",
)
async def get_active_users_by_admin(
    skip: Annotated[int | None, Query(ge=0, description="Entries number to skip")] = 0,
    limit: Annotated[
        int | None, Query(ge=1, le=1000, description="Entries limit")
    ] = 100,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    current_user = await auth_service.get_current_user()

    if UserRole.admin not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users can only be accessed by the admin",
        )

    users = await user_service.get_active_users_by_admin(skip=skip, limit=limit)

    return users
