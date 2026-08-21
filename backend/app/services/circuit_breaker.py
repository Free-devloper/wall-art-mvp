from datetime import datetime
import redis
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class CircuitBreaker:
    @staticmethod
    def _get_daily_key() -> str:
        return f"ai_spend:daily:{datetime.utcnow().strftime('%Y-%m-%d')}"

    @staticmethod
    def _get_monthly_key() -> str:
        return f"ai_spend:monthly:{datetime.utcnow().strftime('%Y-%m')}"

    @staticmethod
    def record_spend(amount_usd: float):
        daily_key = CircuitBreaker._get_daily_key()
        monthly_key = CircuitBreaker._get_monthly_key()
        
        redis_client.incrbyfloat(daily_key, amount_usd)
        redis_client.expire(daily_key, 86400 * 2) # 2 days
        
        redis_client.incrbyfloat(monthly_key, amount_usd)
        redis_client.expire(monthly_key, 86400 * 32) # ~1 month

    @staticmethod
    def check_budget() -> tuple[bool, float, float]:
        daily_key = CircuitBreaker._get_daily_key()
        monthly_key = CircuitBreaker._get_monthly_key()
        
        daily_spent = float(redis_client.get(daily_key) or 0.0)
        monthly_spent = float(redis_client.get(monthly_key) or 0.0)
        
        allowed = (
            daily_spent < settings.DAILY_AI_SPEND_CAP_USD and
            monthly_spent < settings.MONTHLY_AI_SPEND_CAP_USD
        )
        
        return allowed, daily_spent, monthly_spent
