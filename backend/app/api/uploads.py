from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
from app.database import get_db
from app.schemas.upload import UploadRequest, PresignedUrlResponse
from app.models.upload import Upload
from app.services.s3_service import storage_service
from app.services.rate_limiter import RateLimiter
from app.config import settings

router = APIRouter()

@router.post("", response_model=PresignedUrlResponse)
async def create_upload(request: Request, upload_req: UploadRequest, db: AsyncSession = Depends(get_db)):
    if not upload_req.consent_confirmed:
        raise HTTPException(status_code=400, detail="Consent must be confirmed")
        
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{upload_req.customer_email}:{client_ip}"
    allowed, _, retry = RateLimiter.check_rate_limit(rate_key, 5, 3600)
    
    if not allowed:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Try again in {retry} seconds")
        
    upload_id = uuid.uuid4()
    s3_key = f"uploads/{datetime.utcnow().strftime('%Y/%m/%d')}/{upload_id}.jpg"
    
    # We enforce JPEG in content type for simplicity, adjust if needed
    content_type = "image/jpeg"
    max_size = 20 * 1024 * 1024 # 20MB
    
    presigned = storage_service.generate_presigned_upload_url(s3_key, content_type, max_size)
    
    upload = Upload(
        id=upload_id,
        s3_key_original=s3_key,
        original_filename=f"{upload_id}.jpg",
        file_size_bytes=0, # will be known post-upload
        content_type=content_type,
        consent_confirmed_at=datetime.utcnow(),
        customer_email=upload_req.customer_email
    )
    db.add(upload)
    await db.commit()
    
    return PresignedUrlResponse(
        upload_url=presigned['url'],
        upload_id=upload_id,
        fields=presigned.get('fields', {})
    )
