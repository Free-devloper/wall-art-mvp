import asyncio
from datetime import datetime, timedelta
import logging
from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.upload import Upload
from app.models.generation import Generation
from app.models.audit_log import AuditLog
from app.services.s3_service import storage_service
from app.config import settings
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def async_cleanup():
    cutoff = datetime.utcnow() - timedelta(days=settings.RETENTION_DAYS)

    async with AsyncSessionLocal() as db:
        # Find old uploads
        uploads_res = await db.execute(select(Upload).where(Upload.created_at < cutoff))
        uploads = uploads_res.scalars().all()

        keys_to_delete = []
        for u in uploads:
            keys_to_delete.append(u.s3_key_original)
            # Anonymize or delete
            u.customer_email = "redacted@example.com"

        # Find old generations
        gens_res = await db.execute(select(Generation).where(Generation.created_at < cutoff))
        gens = gens_res.scalars().all()

        for g in gens:
            if g.s3_key_preview:
                keys_to_delete.append(g.s3_key_preview)
            if g.s3_key_production:
                keys_to_delete.append(g.s3_key_production)

        if keys_to_delete:
            try:
                storage_service.delete_objects(keys_to_delete)
                audit = AuditLog(
                    actor_type="system", action="retention_cleanup", details={"deleted_keys_count": len(keys_to_delete)}
                )
                db.add(audit)
            except Exception as e:
                logger.error(f"Failed to delete S3 objects during cleanup: {e}")

        await db.commit()


@celery_app.task(name="app.workers.retention_worker.cleanup_expired_data")
def cleanup_expired_data():
    asyncio.run(async_cleanup())
