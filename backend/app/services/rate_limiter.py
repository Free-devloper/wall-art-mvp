import time
import redis
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RateLimiter:
    @staticmethod
    def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> tuple[bool, int, int | None]:
        """
        Uses Redis to track rate limits using sliding window log or simple INCR.
        Here we use simple INCR with EXPIRE.
        """
        current_time = int(time.time())
        window_key = f"rate_limit:{key}:{current_time // window_seconds}"

        count = redis_client.incr(window_key)
        if count == 1:
            redis_client.expire(window_key, window_seconds)

        remaining = max(0, max_requests - count)

        if count > max_requests:
            retry_after = window_seconds - (current_time % window_seconds)
            return False, 0, retry_after

        return True, remaining, None
