from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status

from src.configs.app import settings
from src.models.user import User
from src.schemas.auth_schema import RefreshRequest, SigninRequest, SigninResponse
from src.schemas.user_schema import UserResponse, UserSignup
from src.services.auth_service import AuthService, get_auth_service, get_req_service
from src.services.user_service import UserService, get_user_service

router = APIRouter()


@router.post("/signup", response_model=UserResponse, summary="User signup")
async def signup(
    data: Annotated[UserSignup, Form()],
    service: UserService = Depends(get_user_service),
) -> User:
    res = await service.create_user(data)

    return res


@router.post("/signin", response_model=SigninResponse, summary="User signin")
async def signin(
    data: Annotated[SigninRequest, Form()],
    service: AuthService = Depends(get_req_service),
):
    user = await service.authenticate_user(data.email, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    access_token = service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = service.create_refresh_token()
    await service.store_refresh_token(user.email, refresh_token)  # type: ignore

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=SigninResponse, summary="Refresh tokens")
async def refresh(
    data: Annotated[RefreshRequest, Form()],
    service: AuthService = Depends(get_req_service),
):
    user_email = await service.validate_refresh_token(data.refresh_token)
    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    access_token = service.create_access_token(
        data={"sub": user_email}, expires_delta=access_token_expires
    )
    refresh_token = service.create_refresh_token()
    await service.store_refresh_token(user_email, refresh_token)  # type: ignore

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/users/me/", response_model=UserResponse)
async def get_user_me(
    service: AuthService = Depends(get_auth_service),
):
    current_user = await service.get_current_user()

    return current_user
