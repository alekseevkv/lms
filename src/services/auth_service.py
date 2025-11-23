from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.configs.app import settings
from src.models.user import User
from src.repositories.user import UserRepository, get_user_repository

security = HTTPBearer()


class AuthService:
    def __init__(
        self,
        repo: UserRepository,
        credentials: HTTPAuthorizationCredentials | None = None,
    ):
        self.repo = repo
        self.pwd_context = CryptContext(schemes=["sha512_crypt"])
        self.credentials = credentials

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.repo.get_by_email(email)

        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        data.update({"exp": expire})

        encoded_jwt = jwt.encode(
            data,
            settings.auth.secret_key,
            algorithm=settings.auth.algorithm,
        )
        return encoded_jwt

    async def get_current_user(
        self,
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        if self.credentials is None:
            raise credentials_exception

        try:
            payload = jwt.decode(
                self.credentials.credentials,
                settings.auth.secret_key,
                algorithms=[settings.auth.algorithm],
            )
            email: str | None = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await self.repo.get_by_email(email)
        if user is None:
            raise credentials_exception
        if user.archived is True:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user


async def get_req_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repo)


async def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthService:
    return AuthService(repo, credentials)
