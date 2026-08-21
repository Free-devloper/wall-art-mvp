from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from datetime import datetime, timedelta
from app.database import get_db
from app.models.generation import Generation
from app.auth.auth import get_current_admin

router = APIRouter()


@router.get("")
async def get_costs(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Total spent today
    today_result = await db.scalar(
        select(func.coalesce(func.sum(Generation.cost_usd), 0.0)).where(Generation.completed_at >= today_start)
    )

    # Total spent this month
    month_result = await db.scalar(
        select(func.coalesce(func.sum(Generation.cost_usd), 0.0)).where(Generation.completed_at >= month_start)
    )

    # Average cost per generation
    avg_result = await db.scalar(select(func.coalesce(func.avg(Generation.cost_usd), 0.0)))

    # Daily spend for last 30 days
    thirty_days_ago = now - timedelta(days=30)
    daily_query = await db.execute(
        select(cast(Generation.completed_at, Date).label("day"), func.sum(Generation.cost_usd).label("total"))
        .where(Generation.completed_at >= thirty_days_ago)
        .group_by(cast(Generation.completed_at, Date))
        .order_by(cast(Generation.completed_at, Date))
    )
    daily_spend = [{"date": str(row.day), "total": float(row.total)} for row in daily_query.all()]

    # Per theme spend
    theme_query = await db.execute(
        select(Generation.theme_id, func.sum(Generation.cost_usd).label("total"))
        .where(Generation.cost_usd.isnot(None))
        .group_by(Generation.theme_id)
    )
    per_theme = {str(row.theme_id): float(row.total) for row in theme_query.all()}

    return {
        "total_today": float(today_result),
        "total_this_month": float(month_result),
        "average_cost": float(avg_result),
        "daily_spend": daily_spend,
        "per_theme": per_theme,
    }
