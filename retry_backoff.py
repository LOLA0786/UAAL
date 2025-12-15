"""
Retry utilities with exponential backoff.
Used by workers and delivery layer.
"""

import time
import functools


def with_retry(
    retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
):
    """
    Decorator to retry a function with exponential backoff.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt >= retries:
                        break
                    time.sleep(min(delay, max_delay))
                    delay *= 2
            raise last_exc

        return wrapper

    return decorator
