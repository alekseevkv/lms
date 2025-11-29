from redis.asyncio import Redis

_redis_client: Redis | None = None


def set_redis_client(client: Redis) -> None:
    global _redis_client
    _redis_client = client


def get_redis_client() -> Redis:
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return _redis_client
