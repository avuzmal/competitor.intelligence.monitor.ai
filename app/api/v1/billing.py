from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.client import Client
from app.services.stripe_service import create_checkout_session, handle_webhook_event
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])

@router.post("/checkout/{client_id}", status_code=200)
def initiate_checkout(client_id: int, db: Session = Depends(get_db)):
    """
    Returns a Stripe Checkout URL for a given client to subscribe.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
        
    checkout_url = create_checkout_session(client.email_address, client.id)
    return {"checkout_url": checkout_url}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe Webhook endpoint. Uses raw request body to verify the signature.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature header.")
        
    handle_webhook_event(payload, sig_header, db)
    return {"status": "success"}
