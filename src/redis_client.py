import redis.asyncio as redis

from src.configs.app import settings

redis_client = redis.Redis(
    host=settings.redis.redis_host,
    port=settings.redis.redis_port,
    db=settings.redis.redis_db,
    password=settings.redis.redis_password or None,
    decode_responses=True,
)
