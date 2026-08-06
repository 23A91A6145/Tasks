import time
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from app.utils import logger, log_error

# Simple in-memory rate limiter: IP -> (count, reset_time)
rate_limit_db: Dict[str, Tuple[int, float]] = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    Restricts endpoints to 60 requests per minute per IP address.
    """
    def __init__(self, app, limit: int = 60, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next) -> Response:
        ip = request.client.host if request.client else "unknown"
        
        # Exclude static files or CSS/JS from rate limits to avoid UI lagging
        if request.url.path.startswith(("/static", "/favicon.ico")):
            return await call_next(request)
            
        now = time.time()
        
        if ip not in rate_limit_db:
            rate_limit_db[ip] = (1, now + self.window)
        else:
            count, reset_time = rate_limit_db[ip]
            if now > reset_time:
                rate_limit_db[ip] = (1, now + self.window)
            else:
                if count >= self.limit:
                    log_error(f"Rate limit exceeded by IP: {ip} for path {request.url.path}")
                    return Response(
                        content='{"error": "Too Many Requests", "message": "Rate limit exceeded. Please try again later."}',
                        status_code=429,
                        media_type="application/json"
                    )
                rate_limit_db[ip] = (count + 1, reset_time)
                
        return await call_next(request)
