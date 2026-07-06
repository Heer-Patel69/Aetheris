import hmac
import hashlib
import time
import hashlib
from typing import Dict, List, Tuple, Any
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from microservice.database import get_db, init_db, WebhookDelivery

app = FastAPI(title="Cryptographic Web-Hook Validator Microservice")

# Initialize database schema tables on startup
init_db()

# Rate limiting settings: Max 5 requests per 10 seconds per IP hash
RATE_LIMIT_WINDOW_SECONDS = 10
RATE_LIMIT_MAX_REQUESTS = 5
ip_rate_limit_cache: Dict[str, List[float]] = {}

# Set local HMAC validation secret key
WEBHOOK_SECRET = b"secure-aetheris-validator-secret-token"

# Allow CORS for dashboard views
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Applies strict security hardening headers to all HTTP responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    return response

def verify_rate_limit(ip_hash: str) -> bool:
    """Verifies and updates rate limiting thresholds for an IP address hash."""
    now = time.time()
    if ip_hash not in ip_rate_limit_cache:
        ip_rate_limit_cache[ip_hash] = [now]
        return True

    # Filter timestamps outside the rolling window
    timestamps = [t for t in ip_rate_limit_cache[ip_hash] if now - t < RATE_LIMIT_WINDOW_SECONDS]
    ip_rate_limit_cache[ip_hash] = timestamps

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return False

    ip_rate_limit_cache[ip_hash].append(now)
    return True

@app.post("/webhook", response_model=Dict[str, str])
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Ingests and validates cryptographic webhooks.
    Applies timing-safe HMAC checks, rate-limiting, and logging.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()

    # 1. Rate Limiting Check
    if not verify_rate_limit(ip_hash):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Too many requests from this IP."
        )

    # 2. Extract Headers and Payload
    signature_header = request.headers.get("X-Webhook-Signature")
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing cryptographic verification signature header."
        )

    raw_payload = await request.body()
    payload_str = raw_payload.decode("utf-8", errors="ignore")

    # 3. Cryptographic HMAC-SHA256 Signature Verification
    # Use hmac.compare_digest to prevent timing-attack information leaks
    computed_hmac = hmac.new(WEBHOOK_SECRET, raw_payload, hashlib.sha256).hexdigest()
    
    is_valid = hmac.compare_digest(computed_hmac, signature_header)
    processing_status = "verified" if is_valid else "failed"

    # 4. Log Delivery Record to SQLite database
    delivery_record = WebhookDelivery(
        payload=payload_str,
        source_ip_hash=ip_hash,
        signature=signature_header,
        processing_status=processing_status
    )
    db.add(delivery_record)
    db.commit()
    db.refresh(delivery_record)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid cryptographic webhook signature."
        )

    return {"status": "success", "delivery_id": str(delivery_record.id)}

@app.get("/telemetry", response_model=Dict[str, Any])
async def get_telemetry_metrics(db: Session = Depends(get_db)):
    """Exposes core telemetry data for dashboard visualization."""
    total = db.query(WebhookDelivery).count()
    verified = db.query(WebhookDelivery).filter(WebhookDelivery.processing_status == "verified").count()
    failed = db.query(WebhookDelivery).filter(WebhookDelivery.processing_status == "failed").count()
    
    # Get last 5 webhook delivery runs
    recent_records = db.query(WebhookDelivery).order_by(WebhookDelivery.delivered_at.desc()).limit(5).all()
    recent = [{
        "id": r.id,
        "ip_hash_short": r.source_ip_hash[:8],
        "status": r.processing_status,
        "timestamp": r.delivered_at.isoformat()
    } for r in recent_records]

    return {
        "total_deliveries": total,
        "verified_deliveries": verified,
        "failed_deliveries": failed,
        "recent_activity": recent
    }
