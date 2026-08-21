from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime
from .order import OrderResponse


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    token: str


class AdminOrderListParams(BaseModel):
    status: Optional[str] = None
    customer_email: Optional[str] = None
    page: int = 1
    size: int = 20


class AdminCostReport(BaseModel):
    total_spent: float
    per_day: dict[str, float]
    per_theme: dict[str, float]
    average_cost_per_generation: float


class AdminOrderDetail(OrderResponse):
    upload_url: Optional[str] = None
    generations: List[dict]

    class Config:
        from_attributes = True
