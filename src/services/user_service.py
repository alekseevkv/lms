from uuid import UUID

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

from src.models.user import User
from src.repositories.user import UserRepository, get_user_repository
from src.schemas.user_schema import UserSignup


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.pwd_context = CryptContext(schemes=["argon2"])

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        user = await self.repo.get_by_id(user_id)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        user = await self.repo.get_by_email(email)
        return user

    async def create_user(self, user_data: UserSignup) -> User:
        if await self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        data_dump = user_data.model_dump()
        data_dump["password"] = self.get_password_hash(data_dump["password"])
        user = await self.repo.create(data_dump)

        return user


async def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)
