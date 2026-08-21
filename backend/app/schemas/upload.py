from pydantic import BaseModel, EmailStr, UUID4
from typing import Dict, Any

class UploadRequest(BaseModel):
    consent_confirmed: bool
    customer_email: EmailStr

class PresignedUrlResponse(BaseModel):
    upload_url: str
    upload_id: UUID4
    fields: Dict[str, Any]

class UploadResponse(BaseModel):
    id: UUID4
    original_filename: str
    file_size_bytes: int
    content_type: str
    customer_email: EmailStr
    
    class Config:
        from_attributes = True
