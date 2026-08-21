from pydantic import BaseModel, UUID4
from typing import Optional


class GenerationStatusResponse(BaseModel):
    status: str
    preview_url: Optional[str] = None
    remaining_regenerations: int


class GenerateRequest(BaseModel):
    instructions: Optional[str] = None


class RegenerateRequest(BaseModel):
    reason: Optional[str] = None
