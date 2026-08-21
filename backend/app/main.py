import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.api import themes, uploads, orders, webhooks
from app.api.admin import (
    auth as admin_auth,
    themes as admin_themes,
    orders as admin_orders,
    costs as admin_costs,
    users as admin_users,
)
from app.middleware.logging_middleware import LoggingMiddleware
from app.models.admin_user import AdminUser
from app.auth.auth import hash_password

logger = logging.getLogger(__name__)

# --- Sentry (optional) ---
if settings.SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        traces_sample_rate=1.0,
    )

app = FastAPI(
    title="Wall Art API",
    description="AI-powered custom vinyl wall graphics platform",
    version="1.0.0",
)

from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    logger.error(f"Unhandled error: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__}
    )

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# --- Customer API Routes ---
app.include_router(themes.router, prefix="/api/themes", tags=["themes"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

# --- Admin API Routes ---
app.include_router(admin_auth.router, prefix="/api/admin/auth", tags=["admin-auth"])
app.include_router(admin_themes.router, prefix="/api/admin/themes", tags=["admin-themes"])
app.include_router(admin_orders.router, prefix="/api/admin/orders", tags=["admin-orders"])
app.include_router(admin_costs.router, prefix="/api/admin/costs", tags=["admin-costs"])
app.include_router(admin_users.router, prefix="/api/admin/users", tags=["admin-users"])

# --- Local Storage Routes (dev only) ---
if settings.use_local_storage:
    from app.api.local_storage import router as local_storage_router

    app.include_router(
        local_storage_router,
        prefix="/api/local-storage",
        tags=["local-storage"],
    )
    logger.info("Local storage routes mounted at /api/local-storage (dev mode)")


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting Wall Art API (env={settings.APP_ENV}, storage={settings.STORAGE_MODE})")

    # Create all tables (dev convenience — use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create default admin user if it doesn't exist
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AdminUser).where(AdminUser.email == settings.ADMIN_DEFAULT_EMAIL)
        )
        admin = result.scalar_one_or_none()
        if not admin:
            new_admin = AdminUser(
                email=settings.ADMIN_DEFAULT_EMAIL,
                hashed_password=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
                role="superadmin",
            )
            db.add(new_admin)
            await db.commit()
            logger.info(f"Default admin user created: {settings.ADMIN_DEFAULT_EMAIL}")

    # Auto-seed themes in dev mode so the gallery isn't empty
    if settings.APP_ENV == "development":
        from app.seed_themes import seed as seed_themes
        await seed_themes()


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "storage_mode": settings.STORAGE_MODE,
    }

