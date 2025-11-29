from uuid import UUID

from fastapi import Depends
from redis.asyncio import Redis

from src.redis_client import get_redis_client


class AuthRepository:
    def __init__(self, db: Redis):
        self.db = db

    async def save_refresh_token(
        self, token_hash: str, expires_sec: int, user_id: UUID
    ):
        await self.db.setex(f"rt:{token_hash}", expires_sec, str(user_id))
        await self.db.sadd(f"u_rt:{user_id}", token_hash)  # type: ignore
        await self.db.expire(f"u_rt:{user_id}", expires_sec + 3600)


async def get_auth_repository(
    db: Redis = Depends(get_redis_client),
) -> AuthRepository:
    return AuthRepository(db)
