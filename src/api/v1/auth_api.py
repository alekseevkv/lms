from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from src.configs.app import settings
from src.models.user import User
from src.schemas.auth_schema import (
    LogoutResponse,
    RefreshRequest,
    SigninRequest,
    SigninResponse,
)
from src.schemas.user_schema import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    UserResponse,
    UserSignupRequest,
)
from src.services.auth_service import AuthService, get_auth_service, get_req_service
from src.services.user_service import UserService, get_user_service

router = APIRouter()


@router.post("/signup", response_model=UserResponse, summary="User signup")
async def signup(
    data: UserSignupRequest,
    service: UserService = Depends(get_user_service),
) -> User:
    res = await service.create_user(data)

    return res


@router.post("/signin", response_model=SigninResponse, summary="User signin")
async def signin(
    data: SigninRequest,
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
    await service.store_refresh_token(user.email, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=SigninResponse, summary="Refresh tokens")
async def refresh(
    data: RefreshRequest,
    service: AuthService = Depends(get_req_service),
):
    user_email = await service.validate_refresh_token(data.refresh_token)
    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    access_token = service.create_access_token(
        data={"sub": user_email}, expires_delta=access_token_expires
    )
    refresh_token = service.create_refresh_token()
    await service.store_refresh_token(user_email, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/logout", response_model=LogoutResponse, summary="Logout")
async def logout(
    service: AuthService = Depends(get_auth_service),
):
    current_user = await service.get_current_user()
    await service.revoke_all_refresh_tokens(current_user.email)
    return {"msg": "OK"}


@router.get("/users/me/", response_model=UserResponse, summary="Get current user info")
async def get_user_me(
    service: AuthService = Depends(get_auth_service),
):
    current_user = await service.get_current_user()

    return current_user


@router.post(
    "/change-password", response_model=ChangePasswordResponse, summary="Change password"
)
async def change_password(
    data: ChangePasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    current_user = await auth_service.get_current_user()

    success = await user_service.change_password(
        user=current_user,
        old_password=data.old_password,
        new_password=data.new_password,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    return {"msg": "Password changed successfully"}
