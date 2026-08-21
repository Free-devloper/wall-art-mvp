import io
from PIL import Image


class FaceDetectionService:
    @staticmethod
    def validate_upload(image_bytes: bytes) -> tuple[bool, str | None]:
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                # 1. Resolution check
                width, height = img.size
                if width < 512 or height < 512:
                    return False, f"Image resolution too low ({width}x{height}). Minimum is 512x512."

                # 2. File size check (handled mainly at API layer via content-length, but can be done here)
                if len(image_bytes) > 20 * 1024 * 1024:  # 20MB
                    return False, "File size exceeds 20MB limit."

                # 3. Simple Face Detection Heuristic (placeholder for actual CV/OpenCV logic)
                # In a real app, you would use opencv or face_recognition here.
                # For this implementation, we will assume pass if image opens correctly.
                return True, None

        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
