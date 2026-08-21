import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.generation import Generation
from app.models.order import Order
from app.models.theme import Theme
from app.schemas.generation import GenerationStatusResponse
from app.workers.generation_worker import run_generation_pipeline
from app.services.s3_service import storage_service
from fastapi import HTTPException

class GenerationService:
    @staticmethod
    async def enqueue_generation(
        db: AsyncSession, 
        order_id: uuid.UUID, 
        upload_id: uuid.UUID, 
        theme_id: uuid.UUID, 
        instructions: str | None
    ) -> uuid.UUID:
        
        generation = Generation(
            order_id=order_id,
            upload_id=upload_id,
            theme_id=theme_id,
            instructions_text=instructions,
            status="queued",
            provider="replicate",
            model_version="default"
        )
        db.add(generation)
        await db.commit()
        await db.refresh(generation)
        
        # Enqueue celery task
        run_generation_pipeline.delay(str(generation.id))
        
        return generation.id

    @staticmethod
    async def get_generation_status(db: AsyncSession, order_id: uuid.UUID) -> GenerationStatusResponse:
        # Get latest generation
        result = await db.execute(
            select(Generation)
            .where(Generation.order_id == order_id)
            .order_by(Generation.created_at.desc())
            .limit(1)
        )
        generation = result.scalar_one_or_none()
        
        if not generation:
            raise HTTPException(status_code=404, detail="No generation found for this order")
            
        # Get max regenerations from theme
        order_res = await db.execute(select(Order).where(Order.id == order_id))
        order = order_res.scalar_one()
        
        theme_res = await db.execute(select(Theme).where(Theme.id == order.theme_id))
        theme = theme_res.scalar_one()
        
        # Count existing generations
        count_res = await db.execute(
            select(func.count(Generation.id))
            .where(Generation.order_id == order_id)
        )
        count = count_res.scalar()
        
        remaining = max(0, theme.max_regenerations - count)
        
        preview_url = None
        if generation.s3_key_preview:
            preview_url = storage_service.generate_presigned_download_url(generation.s3_key_preview)

        return GenerationStatusResponse(
            status=generation.status,
            preview_url=preview_url,
            remaining_regenerations=remaining
        )

    @staticmethod
    async def can_regenerate(db: AsyncSession, order_id: uuid.UUID) -> bool:
        order_res = await db.execute(select(Order).where(Order.id == order_id))
        order = order_res.scalar_one_or_none()
        if not order:
            return False
            
        theme_res = await db.execute(select(Theme).where(Theme.id == order.theme_id))
        theme = theme_res.scalar_one()
        
        count_res = await db.execute(
            select(func.count(Generation.id))
            .where(Generation.order_id == order_id)
        )
        count = count_res.scalar()
        
        return count < theme.max_regenerations
