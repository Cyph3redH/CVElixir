import os
import redis.asyncio as redis

REDIS_URL = f"redis://:{os.getenv('REDIS_PASSWORD')}@redis:6379/0"

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def is_cve_sent(cve_id: str) -> bool:
    """Проверяет, была ли уже отправлена эта CVE."""
    return await redis_client.exists(f"sent_cve:{cve_id}") > 0

async def mark_cve_sent(cve_id: str, ttl: int = 604800):  # 7 дней
    """Помечает CVE как отправленную на TTL секунд."""
    await redis_client.setex(f"sent_cve:{cve_id}", ttl, "1")