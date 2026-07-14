import stripe
import structlog
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.config import settings
from app.models.client import Client

logger = structlog.get_logger(__name__)

# Initialize Stripe API Key
stripe.api_key = settings.stripe_secret_key

def create_checkout_session(client_email: str, client_id: int) -> str:
    """
    Creates a Stripe Checkout Session for the recurring $300/mo product.
    Returns the session URL.
    """
    if not settings.stripe_secret_key or not settings.stripe_price_id:
        logger.error("Stripe configuration missing")
        raise HTTPException(status_code=500, detail="Billing is not properly configured.")
        
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': settings.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=client_email,
            client_reference_id=str(client_id),
            success_url="https://your-domain.com/dashboard/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://your-domain.com/dashboard/cancel",
        )
        return session.url
    except Exception as e:
        logger.error("Failed to create Stripe Checkout session", error=str(e), client_id=client_id)
        raise HTTPException(status_code=500, detail="Failed to initialize checkout.")

def handle_webhook_event(payload: bytes, sig_header: str, db: Session) -> None:
    """
    Verifies and handles incoming Stripe webhook events.
    """
    if not settings.stripe_webhook_secret:
        logger.error("Stripe Webhook Secret not configured")
        raise HTTPException(status_code=500, detail="Webhook configuration missing.")
        
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError as e:
        logger.warning("Invalid payload in Stripe webhook", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.warning("Invalid signature in Stripe webhook", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid signature")

    logger.info("Received Stripe Webhook", event_type=event['type'])

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        client_id_str = session.get('client_reference_id')
        customer_id = session.get('customer')
        
        if client_id_str and customer_id:
            try:
                client_id = int(client_id_str)
                client = db.query(Client).filter(Client.id == client_id).first()
                if client:
                    client.is_active = True
                    client.stripe_customer_id = customer_id
                    db.commit()
                    logger.info("Client activated successfully via Stripe", client_id=client.id)
            except ValueError:
                logger.error("Invalid client_reference_id in session", client_reference_id=client_id_str)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        
        if customer_id:
            client = db.query(Client).filter(Client.stripe_customer_id == customer_id).first()
            if client:
                client.is_active = False
                db.commit()
                logger.info("Client deactivated due to canceled subscription", client_id=client.id)
