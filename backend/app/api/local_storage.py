"""Local storage routes for development.

Provides file upload and download endpoints that replace S3 presigned
URLs when STORAGE_MODE=local.  These routes are only mounted in
development — in production, S3 presigned URLs handle everything.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.services.s3_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def local_upload(
    file: UploadFile = File(...),
    key: str = Form(...),
):
    """Accept a file upload and store it locally under the given key.

    The frontend sends the file here instead of to an S3 presigned URL
    when running in local dev mode.
    """
    if not settings.use_local_storage:
        raise HTTPException(status_code=404, detail="Local storage is disabled")

    contents = await file.read()

    max_size = 20 * 1024 * 1024  # 20 MB
    if len(contents) > max_size:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    storage_service.upload_bytes(key, contents, content_type=file.content_type)
    logger.info(f"Local upload: {key} ({len(contents)} bytes)")

    return {"key": key, "size": len(contents)}


@router.get("/files/{file_path:path}")
async def local_download(file_path: str):
    """Serve a file from local storage.

    This replaces S3 presigned download URLs in local dev mode.
    """
    if not settings.use_local_storage:
        raise HTTPException(status_code=404, detail="Local storage is disabled")

    full_path = Path(settings.LOCAL_STORAGE_DIR) / file_path

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Prevent path traversal
    try:
        full_path.resolve().relative_to(Path(settings.LOCAL_STORAGE_DIR).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    # Guess content type from extension
    suffix = full_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }
    media_type = media_types.get(suffix, "application/octet-stream")

    return FileResponse(
        path=str(full_path),
        media_type=media_type,
        filename=full_path.name,
    )
