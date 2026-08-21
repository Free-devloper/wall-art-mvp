from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from app.database import get_db
from app.auth.auth import get_current_admin
from app.models.admin_user import AdminUser
from app.models.theme import Theme
from app.schemas.theme import ThemeResponse, ThemeCreate, ThemeUpdate

router = APIRouter()

@router.get("", response_model=List[ThemeResponse])
async def list_themes(db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(get_current_admin)):
    result = await db.execute(select(Theme).order_by(Theme.sort_order))
    return result.scalars().all()

@router.post("", response_model=ThemeResponse)
async def create_theme(
    theme: ThemeCreate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    new_theme = Theme(**theme.model_dump())
    db.add(new_theme)
    await db.commit()
    await db.refresh(new_theme)
    return new_theme

@router.patch("/{id}", response_model=ThemeResponse)
async def update_theme(
    id: uuid.UUID,
    update_data: ThemeUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    theme = await db.scalar(select(Theme).where(Theme.id == id))
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
        
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(theme, key, value)
        
    await db.commit()
    await db.refresh(theme)
    return theme

@router.delete("/{id}")
async def delete_theme(id: uuid.UUID, db: AsyncSession = Depends(get_db), admin = Depends(get_current_admin)):
    theme = await db.scalar(select(Theme).where(Theme.id == id))
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    await db.delete(theme)
    await db.commit()
    return {"message": "Theme deleted"}
