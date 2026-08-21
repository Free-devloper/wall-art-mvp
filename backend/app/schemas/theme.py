from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


class ThemeBase(BaseModel):
    name: str
    description: str
    prompt_template: str
    example_image_url: Optional[str] = None
    active: bool = True
    sort_order: int = 0
    price_cents: int
    max_regenerations: int = 3


class ThemeCreate(ThemeBase):
    pass


class ThemeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_template: Optional[str] = None
    example_image_url: Optional[str] = None
    active: Optional[bool] = None
    sort_order: Optional[int] = None
    price_cents: Optional[int] = None
    max_regenerations: Optional[int] = None


class ThemeResponse(ThemeBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
