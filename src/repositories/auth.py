from fastapi import Depends
from redis.asyncio import Redis

from src.redis_client import get_redis_client


class AuthRepository:
    def __init__(self, db: Redis):
        self.db = db

    async def add_key_value_with_exp(self, key: str, value: str, exp: int) -> None:
        await self.db.setex(key, exp, value)

    async def add_set_value(self, set_name: str, value: str) -> None:
        await self.db.sadd(set_name, value)  # type: ignore

    async def add_set_exp(self, set_name: str, exp: int) -> None:
        await self.db.expire(set_name, exp)

    async def get_by_key(self, key: str) -> str | None:
        value = await self.db.get(key)
        return value

    async def get_set(self, set_name: str):
        set_members = await self.db.smembers(set_name)  # type: ignore
        return set_members

    async def delete(self, *key: str) -> None:
        await self.db.delete(*key)

    async def delete_from_set(self, set_name: str, value: str) -> None:
        await self.db.srem(set_name, value)  # type: ignore


async def get_auth_repository(
    db: Redis = Depends(get_redis_client),
) -> AuthRepository:
    return AuthRepository(db)
