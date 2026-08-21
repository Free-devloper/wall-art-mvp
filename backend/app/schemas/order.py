from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime


class OrderCreate(BaseModel):
    theme_id: UUID4
    upload_id: UUID4
    instructions: Optional[str] = None
    product_size: str
    customer_email: EmailStr
    customer_name: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str
    production_notes: Optional[str] = None


class CheckoutSessionResponse(BaseModel):
    checkout_url: str


class OrderConfirmation(BaseModel):
    order_id: UUID4
    status: str
    customer_email: str
    total_cents: int


class OrderResponse(BaseModel):
    id: UUID4
    status: str
    theme_id: UUID4
    product_size: str
    price_cents: int
    customer_email: str
    customer_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    size: int
