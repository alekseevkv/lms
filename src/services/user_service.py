from uuid import UUID

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

from src.models.user import User
from src.repositories.user import UserRepository, get_user_repository
from src.schemas.user_schema import UserSignupRequest


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


async def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)
