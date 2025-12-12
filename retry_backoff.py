"""
Retry/backoff helper for UAAL. Uses Redis (if available) for visibility
and Celery for task retries. Provides consistent backoff schedule and
dead-letter pushing hook.
"""
import time
import json
import os
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
try:
    r = redis.from_url(REDIS_URL)
except Exception:
    r = None

BACKOFF_SCHEDULE = [2, 4, 8, 16, 32]  # seconds; Celery also handles retries

def push_retry(payload: dict, attempt: int = 1):
    """Store retry metadata in Redis list for visibility and alerting."""
    entry = {"payload": payload, "attempt": attempt, "ts": time.time()}
    if r:
        r.rpush("uaal:retries", json.dumps(entry))
    return True

def pop_all_retries():
    """Admin helper for reading retry queue (not used in worker)."""
    if not r:
        return []
    items = []
    while True:
        raw = r.lpop("uaal:retries")
        if not raw:
            break
        items.append(json.loads(raw))
    return items
