from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "wallart_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.generation_worker",
        "app.workers.retention_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "cleanup-expired-data-daily": {
        "task": "app.workers.retention_worker.cleanup_expired_data",
        "schedule": crontab(hour=0, minute=0),
    }
}
