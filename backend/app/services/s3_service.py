import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class LocalStorageService:
    """On-server filesystem storage for development.

    Stores files under LOCAL_STORAGE_DIR with subdirectories for
    uploads and generations. Serves files via the backend's
    /files/ static route.
    """

    def __init__(self):
        self.base_dir = Path(settings.LOCAL_STORAGE_DIR)
        self.uploads_dir = self.base_dir / "uploads"
        self.generations_dir = self.base_dir / "generations"
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.generations_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorageService initialized at {self.base_dir}")

    def _resolve_path(self, key: str) -> Path:
        """Resolve a storage key to an absolute file path."""
        return self.base_dir / key

    def generate_presigned_upload_url(self, key: str, content_type: str, max_size_bytes: int) -> dict:
        """Return a local upload endpoint URL.

        In local dev mode the frontend POSTs the file to
        /api/local-storage/upload with the key as a form field.
        """
        return {
            "url": f"{settings.BACKEND_URL}/api/local-storage/upload",
            "fields": {
                "key": key,
                "Content-Type": content_type,
            },
        }

    def generate_presigned_download_url(self, key: str, expiry_seconds: int = 3600) -> str:
        """Return a URL that serves the file from the backend's static route."""
        return f"{settings.BACKEND_URL}/api/local-storage/files/{key}"

    def upload_bytes(self, key: str, data: bytes, content_type: Optional[str] = None) -> str:
        """Write raw bytes to local storage under the given key."""
        path = self._resolve_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        logger.info(f"Stored {len(data)} bytes at {path}")
        return key

    def download_bytes(self, key: str) -> bytes:
        """Read raw bytes from local storage."""
        path = self._resolve_path(key)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        return path.read_bytes()

    def file_exists(self, key: str) -> bool:
        return self._resolve_path(key).exists()

    def delete_object(self, key: str):
        path = self._resolve_path(key)
        if path.exists():
            path.unlink()
            logger.info(f"Deleted {path}")

    def delete_objects(self, keys: list[str]):
        for k in keys:
            self.delete_object(k)

    def list_objects(self, prefix: str) -> list[str]:
        """List all keys under a given prefix."""
        base = self._resolve_path(prefix)
        if not base.exists():
            return []
        return [str(p.relative_to(self.base_dir)).replace("\\", "/") for p in base.rglob("*") if p.is_file()]


class S3StorageService:
    """AWS S3 storage for staging/production."""

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        logger.info("S3StorageService initialized")

    def generate_presigned_upload_url(self, key: str, content_type: str, max_size_bytes: int) -> dict:
        try:
            response = self.s3_client.generate_presigned_post(
                settings.S3_BUCKET_UPLOADS,
                key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 0, max_size_bytes],
                ],
                ExpiresIn=settings.PRESIGNED_URL_EXPIRY_SECONDS,
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned upload URL: {e}")
            raise

    def generate_presigned_download_url(self, key: str, expiry_seconds: int = 3600) -> str:
        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.S3_BUCKET_UPLOADS, "Key": key},
                ExpiresIn=expiry_seconds,
            )
        except ClientError as e:
            logger.error(f"Failed to generate presigned download URL: {e}")
            raise

    def upload_bytes(self, key: str, data: bytes, content_type: Optional[str] = None) -> str:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        self.s3_client.put_object(
            Bucket=settings.S3_BUCKET_GENERATIONS,
            Key=key,
            Body=data,
            **extra_args,
        )
        return key

    def download_bytes(self, key: str) -> bytes:
        response = self.s3_client.get_object(
            Bucket=settings.S3_BUCKET_UPLOADS,
            Key=key,
        )
        return response["Body"].read()

    def file_exists(self, key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=settings.S3_BUCKET_UPLOADS, Key=key)
            return True
        except ClientError:
            return False

    def delete_object(self, key: str):
        try:
            self.s3_client.delete_object(Bucket=settings.S3_BUCKET_UPLOADS, Key=key)
        except ClientError as e:
            logger.error(f"Failed to delete S3 object: {e}")
            raise

    def delete_objects(self, keys: list[str]):
        if not keys:
            return
        try:
            self.s3_client.delete_objects(
                Bucket=settings.S3_BUCKET_UPLOADS,
                Delete={"Objects": [{"Key": k} for k in keys]},
            )
        except ClientError as e:
            logger.error(f"Failed to delete S3 objects: {e}")
            raise

    def list_objects(self, prefix: str) -> list[str]:
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=settings.S3_BUCKET_UPLOADS,
                Prefix=prefix,
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return []


def get_storage_service():
    """Factory: returns the correct storage service based on config."""
    if settings.use_local_storage:
        return LocalStorageService()
    return S3StorageService()


# Singleton instance — import this in other modules
storage_service = get_storage_service()
