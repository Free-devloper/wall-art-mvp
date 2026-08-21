from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = True
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://wallart:wallart_dev_password@postgres:5432/wallart"
    REDIS_URL: str = "redis://redis:6379/0"

    # Storage mode: "local" for on-server filesystem, "s3" for AWS S3
    STORAGE_MODE: str = "local"
    LOCAL_STORAGE_DIR: str = "/app/local_storage"

    # AWS S3 (only used when STORAGE_MODE=s3)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "eu-west-2"
    S3_BUCKET_UPLOADS: str = "wallart-uploads-dev"
    S3_BUCKET_GENERATIONS: str = "wallart-generations-dev"
    PRESIGNED_URL_EXPIRY_SECONDS: int = 900

    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_placeholder"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder"

    # AI Provider
    REPLICATE_API_TOKEN: str = "r8_placeholder"
    AI_PROVIDER: str = "replicate"

    # Email
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "orders@wallart.local"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # AI spend caps
    DAILY_AI_SPEND_CAP_USD: float = 50.0
    MONTHLY_AI_SPEND_CAP_USD: float = 1000.0

    # Data retention
    RETENTION_DAYS: int = 90

    # Auth
    SECRET_KEY: str = "dev-only-secret-change-in-production-abc123xyz"
    ADMIN_DEFAULT_EMAIL: str = "admin@wallart.co.uk"
    ADMIN_DEFAULT_PASSWORD: str = "admin123dev"

    # Clerk Authentication
    CLERK_SECRET_KEY: str = "sk_test_Oi7RttA1FQOVuHQxFcE2L9pBdC9leAP9VlZ3r8n9aT"
    CLERK_JWKS_URL: str = "https://pleasant-salmon-7160.clerk.accounts.dev/.well-known/jwks.json"
    CLERK_ISSUER: str = "https://pleasant-salmon-7160.clerk.accounts.dev"

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    @property
    def use_local_storage(self) -> bool:
        """Whether to use local filesystem instead of S3."""
        return self.STORAGE_MODE == "local" or not self.AWS_ACCESS_KEY_ID

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
