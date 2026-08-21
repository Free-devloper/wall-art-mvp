from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse
from app.models.admin_user import AdminUser
from app.auth.auth import verify_password, create_access_token, get_current_admin

router = APIRouter()


@router.post("/login", response_model=AdminLoginResponse)
async def login(req: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminUser).where(AdminUser.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.email, "role": user.role})
    return AdminLoginResponse(token=token)


@router.get("/me")
async def get_me(admin: AdminUser = Depends(get_current_admin)):
    return {"id": admin.id, "email": admin.email, "role": admin.role}
