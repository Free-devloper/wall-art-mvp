from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid
from app.database import get_db
from app.models.order import Order
from app.models.generation import Generation
from app.models.upload import Upload
from app.models.audit_log import AuditLog
from app.schemas.order import OrderListResponse, OrderResponse, OrderStatusUpdate
from app.schemas.admin import AdminOrderDetail
from app.auth.auth import get_current_admin
from app.models.admin_user import AdminUser
from app.services.s3_service import storage_service

router = APIRouter()


@router.get("", response_model=OrderListResponse)
async def list_orders(
    status: str = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)

    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar()

    query = query.order_by(Order.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()

    return OrderListResponse(items=items, total=total, page=page, size=size)


@router.get("/{id}", response_model=AdminOrderDetail)
async def get_order_detail(
    id: uuid.UUID, db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(get_current_admin)
):
    order = await db.scalar(select(Order).where(Order.id == id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    upload = await db.scalar(select(Upload).where(Upload.order_id == id))
    generations_res = await db.execute(select(Generation).where(Generation.order_id == id))
    generations = generations_res.scalars().all()

    # map to response
    order_dict = order.__dict__.copy()
    if upload:
        order_dict["upload_url"] = storage_service.generate_presigned_download_url(upload.s3_key_original)

    order_dict["generations"] = [
        {
            "id": g.id,
            "status": g.status,
            "cost_usd": g.cost_usd,
            "created_at": g.created_at,
            "preview_url": storage_service.generate_presigned_download_url(g.s3_key_preview)
            if g.s3_key_preview
            else None,
        }
        for g in generations
    ]

    return order_dict


@router.post("/{id}/status")
async def update_status(
    id: uuid.UUID,
    update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    order = await db.scalar(select(Order).where(Order.id == id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not order.is_valid_status_transition(update.status):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    order.status = update.status
    if hasattr(update, "production_notes") and update.production_notes:
        order.production_notes = update.production_notes

    audit = AuditLog(
        actor_type="admin",
        actor_id=str(admin.id),
        action="admin_status_update",
        order_id=order.id,
        details={"status": update.status},
    )
    db.add(audit)
    await db.commit()
    return {"message": "Status updated"}


@router.delete("/{id}/photos")
async def delete_order_photos(
    id: uuid.UUID, db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(get_current_admin)
):
    upload = await db.scalar(select(Upload).where(Upload.order_id == id))
    if upload:
        storage_service.delete_object(upload.s3_key_original)

    generations = await db.scalars(select(Generation).where(Generation.order_id == id))
    for g in generations:
        if g.s3_key_preview:
            storage_service.delete_object(g.s3_key_preview)
        if g.s3_key_production:
            storage_service.delete_object(g.s3_key_production)

    audit = AuditLog(
        actor_type="admin",
        actor_id=str(admin.id),
        action="admin_delete_photos",
        order_id=id,
        details={"action": "Deleted order photos and generations"},
    )
    db.add(audit)
    await db.commit()

    return {"message": "Photos deleted"}


@router.get("/{id}/production-file")
async def get_production_file(
    id: uuid.UUID, db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(get_current_admin)
):
    order = await db.scalar(select(Order).where(Order.id == id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    result = await db.execute(
        select(Generation)
        .where(Generation.order_id == id, Generation.status == "completed")
        .order_by(Generation.created_at.desc())
        .limit(1)
    )
    generation = result.scalar_one_or_none()
    if not generation or not generation.s3_key_production:
        raise HTTPException(status_code=404, detail="No production file available")

    url = storage_service.generate_presigned_download_url(generation.s3_key_production)

    audit = AuditLog(
        actor_type="admin",
        actor_id=str(admin.id),
        action="admin_get_production_file",
        order_id=id,
        details={"file": generation.s3_key_production},
    )
    db.add(audit)
    await db.commit()

    return {"production_url": url}


@router.post("/{id}/regenerate")
async def admin_regenerate(
    id: uuid.UUID, db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(get_current_admin)
):
    order = await db.scalar(select(Order).where(Order.id == id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    upload = await db.scalar(select(Upload).where(Upload.order_id == id))
    if not upload:
        raise HTTPException(status_code=400, detail="No upload linked to order")

    from app.services.generation_service import GenerationService

    await GenerationService.enqueue_generation(db, order.id, upload.id, order.theme_id, "Admin regeneration")

    audit = AuditLog(
        actor_type="admin",
        actor_id=str(admin.id),
        action="admin_regenerate",
        order_id=id,
        details={"action": "Admin triggered regeneration"},
    )
    db.add(audit)
    await db.commit()

    return {"message": "Regeneration queued"}
