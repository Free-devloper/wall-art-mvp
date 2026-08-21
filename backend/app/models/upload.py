import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, ForeignKey
from app.database import Base

class Upload(Base):
    __tablename__ = "uploads"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    s3_key_original: Mapped[str] = mapped_column(String)
    original_filename: Mapped[str] = mapped_column(String)
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String)
    
    consent_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    quality_check_result: Mapped[str] = mapped_column(String, default="pending")
    quality_check_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    
    customer_email: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
