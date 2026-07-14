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
        
    if x_webhook_secret != settings.webhook_secret:
        logger.warning("Unauthorized webhook access attempt", provided_secret=x_webhook_secret)
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
        
    return True
