import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, ForeignKey
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="new")
    theme_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("themes.id"))
    product_size: Mapped[str] = mapped_column(String)
    price_cents: Mapped[int] = mapped_column(Integer)
    
    stripe_payment_id: Mapped[str | None] = mapped_column(String, nullable=True)
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    
    shipping_address_line1: Mapped[str | None] = mapped_column(String, nullable=True)
    shipping_address_line2: Mapped[str | None] = mapped_column(String, nullable=True)
    shipping_city: Mapped[str | None] = mapped_column(String, nullable=True)
    shipping_postcode: Mapped[str | None] = mapped_column(String, nullable=True)
    shipping_country: Mapped[str] = mapped_column(String, default="GB")
    
    customer_email: Mapped[str] = mapped_column(String)
    customer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    
    production_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_valid_status_transition(self, new_status: str) -> bool:
        valid_transitions = {
            "new": ["awaiting_approval", "cancelled"],
            "awaiting_approval": ["paid", "cancelled"],
            "paid": ["in_production", "refunded", "cancelled"],
            "in_production": ["dispatched", "refunded"],
            "dispatched": ["refunded"],
            "cancelled": [],
            "refunded": []
        }
        return new_status in valid_transitions.get(self.status, [])
