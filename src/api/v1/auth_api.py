from typing import Annotated

from fastapi import APIRouter, Depends, Form

from src.models.user import User
from src.schemas.user_schema import UserResponse, UserSignup
from src.services.user_service import UserService, get_user_service

router = APIRouter()


@router.post("/signup", response_model=UserResponse, summary="User signup")
async def signup(
    data: Annotated[UserSignup, Form()],
    service: UserService = Depends(get_user_service),
) -> User:
    res = await service.create_user(data)

    return res
