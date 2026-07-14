import hmac
from fastapi import Header, HTTPException
from typing import Annotated
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)

async def verify_webhook_secret(
    x_webhook_secret: Annotated[str, Header()]
) -> bool:
    """
    Dependency to verify that the incoming webhook matches our configured secret.
    """
    if not settings.webhook_secret:
        logger.error("WEBHOOK_SECRET is not configured!")
        raise HTTPException(status_code=500, detail="Webhook security configuration error.")
        
    if not hmac.compare_digest(x_webhook_secret, settings.webhook_secret):
        logger.warning("Unauthorized webhook access attempt")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
        
    return True
