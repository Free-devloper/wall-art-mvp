from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
import logging
import json

logger = logging.getLogger("api_logger")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request info
        method = request.method
        url = str(request.url)

        # Exclude image data bodies from log
        # Usually we do this by not logging body if Content-Type is multipart/form-data or image

        response = await call_next(request)

        process_time = time.time() - start_time
        status_code = response.status_code

        log_dict = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "process_time_ms": round(process_time * 1000, 2),
        }

        logger.info(json.dumps(log_dict))

        return response
