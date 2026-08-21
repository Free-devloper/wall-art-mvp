"""Admin user management - lists users and their orders."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.order import Order
from app.auth.auth import get_current_admin

router = APIRouter()


@router.get("")
async def list_users(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """List all unique users who have placed orders, with order counts."""
    query = await db.execute(
        select(
            Order.user_id,
            Order.customer_name,
            Order.customer_email,
            func.count(Order.id).label("order_count"),
            func.sum(Order.price_cents).label("total_spent_cents"),
            func.min(Order.created_at).label("first_order"),
            func.max(Order.created_at).label("last_order"),
        )
        .where(Order.customer_email.isnot(None))
        .group_by(Order.user_id, Order.customer_name, Order.customer_email)
        .order_by(func.max(Order.created_at).desc())
    )
    users = []
    for row in query.all():
        users.append(
            {
                "user_id": row.user_id or "anonymous",
                "name": row.customer_name or "Unknown",
                "email": row.customer_email,
                "order_count": row.order_count,
                "total_spent_cents": row.total_spent_cents or 0,
                "first_order": str(row.first_order) if row.first_order else None,
                "last_order": str(row.last_order) if row.last_order else None,
            }
        )
    return {"users": users, "total": len(users)}


@router.get("/{user_id}/orders")
async def get_user_orders(user_id: str, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """Get all orders for a specific user."""
    result = await db.execute(select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()))
    orders = result.scalars().all()
    return {
        "orders": [
            {
                "id": str(o.id),
                "status": o.status,
                "customer_name": o.customer_name,
                "customer_email": o.customer_email,
                "price_cents": o.price_cents,
                "product_size": o.product_size,
                "created_at": str(o.created_at),
            }
            for o in orders
        ]
    }
