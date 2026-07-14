import structlog
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import verify_webhook_secret
from app.api.v1.orchestration import _process_weekly_briefings
from app.models.client import Client

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post(
    "/n8n/trigger-all", 
    status_code=202,
    dependencies=[Depends(verify_webhook_secret)]
)
def trigger_all_briefings_webhook(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Secure webhook for n8n to trigger weekly briefings for all active clients.
    """
    logger.info("Webhook triggered: trigger-all briefings")
    background_tasks.add_task(_process_weekly_briefings, db)
    return {"message": "Weekly briefing orchestration started in the background."}


def _process_single_client_briefing(db: Session, client_id: int):
    """Orchestrates briefing for a single client."""
    client = db.query(Client).filter(Client.id == client_id, Client.is_active == True).first()
    if not client:
        logger.error("Client not found or inactive during background processing", client_id=client_id)
        return
        
    logger.info("Starting weekly briefing for single client", client_id=client_id)
    # We can temporarily patch the _process_weekly_briefings to handle a single client
    # or just use the same logic here. For simplicity, we just fetch this client and run.
    from app.api.v1.orchestration import _process_weekly_briefings
    
    # We create a pseudo-db session or modify _process_weekly_briefings to accept an optional client_id
    # Wait, the prompt says "Triggers the orchestration logic for a single specific client"
    # To keep DRY, let's implement the logic or refactor. But the prompt allows reusing Phase 3 logic.
    # We will just duplicate the loop body for the single client here.
    from typing import Dict, Any
    from app.models.snapshot import Snapshot
    from app.models.briefing_history import BriefingHistory, DeliveryStatus
    from deepdiff import DeepDiff
    from app.api.v1.orchestration import _parse_diff
    from app.services.data_sanitizer import sanitize_delta_for_llm
    from app.services.claude_service import generate_strategic_insights
    from app.services.template_service import render_briefing_email
    from app.services.email_service import send_briefing
    from app.services.slack_service import send_slack_briefing

    client_log = logger.bind(client_id=client.id, client_name=client.name)
    insights_list: List[Dict[str, Any]] = []
    
    for competitor in client.competitors:
        comp_log = client_log.bind(competitor_id=competitor.id, competitor_name=competitor.name)
        
        snapshots = (
            db.query(Snapshot)
            .filter(Snapshot.competitor_id == competitor.id)
            .order_by(Snapshot.scrape_date.desc())
            .limit(2)
            .all()
        )
        
        if not snapshots:
            comp_log.info("Skipping competitor - No snapshots found.")
            continue
            
        if len(snapshots) < 2:
            raw_delta = {
                "added_items": snapshots[0].raw_data,
                "removed_items": {},
                "modified_items": {}
            }
        else:
            diff = DeepDiff(snapshots[1].raw_data, snapshots[0].raw_data, ignore_order=True, report_repetition=True)
            raw_delta = {
                "added_items": _parse_diff(diff, 'dictionary_item_added', 'iterable_item_added'),
                "removed_items": _parse_diff(diff, 'dictionary_item_removed', 'iterable_item_removed'),
                "modified_items": _parse_diff(diff, 'values_changed', 'type_changes')
            }
            
        is_empty = not raw_delta.get("added_items") and not raw_delta.get("removed_items") and not raw_delta.get("modified_items")
        if is_empty:
            comp_log.info("Skipping competitor - No changes.")
            continue
            
        sanitized_text = sanitize_delta_for_llm(raw_delta)
        insight = generate_strategic_insights(competitor_name=competitor.name, sanitized_delta=sanitized_text)
        
        if insight.what_changed or insight.what_it_means or insight.what_to_do:
            insights_list.append({"competitor_name": competitor.name, "insight": insight})
            
            history_record = BriefingHistory(
                client_id=client.id,
                competitor_id=competitor.id,
                insight_json=insight.model_dump(mode="json"),
                delivery_status=DeliveryStatus.SENT
            )
            db.add(history_record)
            
    db.commit()
            
    if insights_list:
        if client.slack_webhook_url:
            send_slack_briefing(client.slack_webhook_url, client.name, insights_list)
            client_log.info("Briefing sent via Slack")
            
        html_content = render_briefing_email(client.name, insights_list)
        send_briefing(client.email_address, client.name, html_content)
        client_log.info("Briefing sent via Email")
    else:
        client_log.info("No insights to send for client")


@router.post(
    "/n8n/trigger-client/{client_id}", 
    status_code=202,
    dependencies=[Depends(verify_webhook_secret)]
)
def trigger_client_briefings_webhook(
    client_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Secure webhook for n8n to trigger a weekly briefing for a specific active client.
    """
    logger.info("Webhook triggered: trigger-client briefing", client_id=client_id)
    background_tasks.add_task(_process_single_client_briefing, db, client_id)
    return {"message": f"Weekly briefing orchestration started for client {client_id}."}
