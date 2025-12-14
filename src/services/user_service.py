from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

from src.models.user import User
from src.repositories.user import UserRepository, get_user_repository
from src.schemas.user_schema import (
    UpdateUserByAdminRequest,
    UpdateUserRequest,
    UserRole,
    UserSignupRequest,
)


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.pwd_context = CryptContext(schemes=["argon2"])

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        user = await self.repo.get_by_id(user_id)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        user = await self.repo.get_by_email(email)
        return user

    async def create_user(self, user_data: UserSignupRequest) -> User:
        if await self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        data_dump = user_data.model_dump()
        data_dump["password"] = self.get_password_hash(data_dump["password"])
        data_dump["roles"] = [UserRole.student]
        user = await self.repo.create(data_dump)

        return user

    async def create_admin(self, user_data: UserSignupRequest) -> User:
        if await self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        data_dump = user_data.model_dump()
        data_dump["password"] = self.get_password_hash(data_dump["password"])
        data_dump["roles"] = [UserRole.admin]
        user = await self.repo.create(data_dump)

        return user

    async def change_password(
        self, user: User, old_password: str, new_password: str
    ) -> bool:
        if not self.verify_password(old_password, user.password):
            return False
        hashed_new = self.get_password_hash(new_password)
        await self.repo.update_password(user, hashed_new)
        return True

    async def update_user(self, user: User, data: UpdateUserRequest) -> User:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if "email" in update_data:
            user.email = update_data["email"]
        if "username" in update_data:
            user.username = update_data["username"]

        if update_data:
            user.update_at = datetime.utcnow()

        updated_user = await self.repo.update(user)

        return updated_user

    async def update_user_by_admin(self, data: UpdateUserByAdminRequest) -> User:
        user = await self.get_user_by_email(data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no user with such credentials",
            )

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if "new_email" in update_data:
            user.email = update_data["new_email"]
        if "username" in update_data:
            user.username = update_data["username"]
        if "roles" in update_data:
            user.roles = update_data["roles"]

        if update_data:
            user.update_at = datetime.utcnow()

        updated_user = await self.repo.update(user)

        return updated_user

    async def delete_user_by_admin(self, user_id: UUID) -> None:
        user = await self.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not exist",
            )

        user.update_at = datetime.utcnow()
        user.archived = True

        await self.repo.update(user)

    async def get_active_users_by_admin(
        self, skip: int | None, limit: int | None
    ) -> Sequence[User]:
        users = await self.repo.get_all_active(skip=skip, limit=limit)

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Users not found",
            )

        return users


async def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)
