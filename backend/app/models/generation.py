import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Numeric, ForeignKey
from app.database import Base

class Generation(Base):
    __tablename__ = "generations"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"))
    upload_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("uploads.id"))
    theme_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("themes.id"))
    
    instructions_text: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="queued") # queued/processing/completed/failed
    provider: Mapped[str] = mapped_column(String)
    model_version: Mapped[str] = mapped_column(String)
    
    s3_key_preview: Mapped[str | None] = mapped_column(String, nullable=True)
    s3_key_production: Mapped[str | None] = mapped_column(String, nullable=True)
    
    cost_usd: Mapped[float] = mapped_column(Numeric(10, 4), default=0.0)
    generation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    failure_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
