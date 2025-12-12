"""Simple retry queue using Redis lists for demo purposes."""
from typing import Dict, Any, Optional
from redis_client import redis_client
import json
import time

RETRY_QUEUE = "uaal:retry:queue"


def push_retry(
    action: Dict[str, Any],
    attempt: int = 1,
    max_attempts: int = 5,
    backoff_secs: Optional[int] = None,
) -> None:
    item = {
        "action": action,
        "attempt": attempt,
        "max_attempts": max_attempts,
        "ts": int(time.time()),
    }
    if backoff_secs is None:
        backoff_secs = min(2 ** (attempt - 1), 300)
    # push to sorted set by execute_at for delayed retries
    execute_at = int(time.time()) + backoff_secs
    redis_client.zadd(RETRY_QUEUE, {json.dumps(item): execute_at})


def fetch_due(limit: int = 10):
    now = int(time.time())
    items = redis_client.zrangebyscore(
        RETRY_QUEUE, 0, now, start=0, num=limit, withscores=False
    )
    result = []
    for it in items:
        try:
            obj = json.loads(it)
            result.append(obj)
            redis_client.zrem(RETRY_QUEUE, it)
        except Exception:
            redis_client.zrem(RETRY_QUEUE, it)
    return result


def retry_count():
    return redis_client.zcard(RETRY_QUEUE)
