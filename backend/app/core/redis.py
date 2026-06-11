import os
import json
import logging
from typing import Optional, Any
from redis.asyncio import Redis, from_url

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client: Optional[Redis] = None


async def init_redis_pool() -> Redis:
    global redis_client
    if redis_client is None:
        logger.info(f"Initializing Redis pool with URL: {REDIS_URL}")
        redis_client = from_url(REDIS_URL, decode_responses=True)
    return redis_client


async def close_redis_pool():
    global redis_client
    if redis_client is not None:
        logger.info("Closing Redis connection pool")
        await redis_client.aclose()
        redis_client = None


def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized. Call init_redis_pool() first.")
    return redis_client


# Session Cache Helper Functions

def get_session_key(session_id: str) -> str:
    return f"draft:session:{session_id}"


async def get_draft_session(session_id: str) -> Optional[dict[str, Any]]:
    client = get_redis()
    key = get_session_key(session_id)
    data = await client.get(key)
    if not data:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        logger.error(f"Failed to decode draft session JSON for key {key}")
        return None


async def save_draft_session(session_id: str, data: dict[str, Any], ttl: int = 86400) -> None:
    client = get_redis()
    key = get_session_key(session_id)
    serialized_data = json.dumps(data)
    await client.set(key, serialized_data, ex=ttl)


async def delete_draft_session(session_id: str) -> None:
    client = get_redis()
    key = get_session_key(session_id)
    await client.delete(key)
