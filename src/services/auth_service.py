import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.configs.app import settings
from src.models.user import User
from src.repositories.auth import AuthRepository, get_auth_repository
from src.repositories.user import UserRepository, get_user_repository

security = HTTPBearer()


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        auth_repo: AuthRepository,
        credentials: HTTPAuthorizationCredentials | None = None,
    ):
        self.user_repo = user_repo
        self.auth_repo = auth_repo
        self.pwd_context = CryptContext(schemes=["sha512_crypt"])
        self.credentials = credentials

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.user_repo.get_by_email(email)

        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        encoding_data = data.copy()
        expire = (
            datetime.utcnow() + expires_delta
            if expires_delta
            else datetime.utcnow() + timedelta(minutes=15)
        )

        encoding_data.update({"exp": expire})

        encoded_jwt = jwt.encode(
            encoding_data,
            settings.auth.secret_key,
            algorithm=settings.auth.algorithm,
        )

        return encoded_jwt

    def create_refresh_token(self) -> str:
        return secrets.token_urlsafe(64)

    def hash_refresh_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def store_refresh_token(self, user_email: str, token: str):
        token_hash = self.hash_refresh_token(token)
        expires_sec = settings.auth.refresh_token_expire_days * 24 * 3600
        refresh_token_set = f"u_rt:{user_email}"
        await self.auth_repo.add_key_value_with_exp(
            f"rt:{token_hash}", user_email, expires_sec
        )
        await self.auth_repo.add_set_value(refresh_token_set, token_hash)
        await self.auth_repo.add_set_exp(refresh_token_set, expires_sec + 3600)

    async def validate_refresh_token(self, token: str) -> str:
        token_hash = self.hash_refresh_token(token)
        key = f"rt:{token_hash}"
        user_email = await self.auth_repo.get_by_key(key)
        if not user_email:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )
        await self.auth_repo.delete(key)
        await self.auth_repo.delete_from_set(f"u_rt:{user_email}", token_hash)
        return user_email

    async def revoke_all_refresh_tokens(self, user_email: str):
        set_name = f"u_rt:{user_email}"
        token_hashes = await self.auth_repo.get_set(set_name)
        if token_hashes:
            keys = [f"rt:{h}" for h in token_hashes]
            await self.auth_repo.delete(*keys)
        await self.auth_repo.delete(set_name)

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

        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise credentials_exception
        if user.archived is True:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user


async def get_req_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_repo: AuthRepository = Depends(get_auth_repository),
) -> AuthService:
    return AuthService(user_repo, auth_repo)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_repo: AuthRepository = Depends(get_auth_repository),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthService:
    return AuthService(user_repo, auth_repo, credentials)
