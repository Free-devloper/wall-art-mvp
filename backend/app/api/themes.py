from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.theme import Theme
from app.schemas.theme import ThemeResponse

router = APIRouter()

@router.get("", response_model=List[ThemeResponse])
async def list_active_themes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Theme).where(Theme.active == True).order_by(Theme.sort_order)
    )
    themes = result.scalars().all()
    return themes
