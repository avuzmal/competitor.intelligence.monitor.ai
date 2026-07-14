import structlog
from typing import List, Dict, Any
from slack_sdk.webhook import WebhookClient
from app.schemas.insights import CompetitorInsight

logger = structlog.get_logger(__name__)

def send_slack_briefing(slack_webhook_url: str, client_name: str, insights_list: List[Dict[str, Any]]) -> bool:
    """
    Sends a formatted weekly briefing to a Slack channel using Block Kit.
    """
    if not slack_webhook_url:
        logger.warning("No Slack webhook URL provided.")
        return False
        
    webhook = WebhookClient(slack_webhook_url)
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚀 Weekly Competitive Briefing: {client_name}",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    
    for item in insights_list:
        comp_name = item.get("competitor_name", "Unknown Competitor")
        insight: CompetitorInsight = item["insight"]
        
        # Determine threat emoji
        if insight.threat_level.value == 'HIGH':
            threat_emoji = "🔴 *High Threat*"
        elif insight.threat_level.value == 'MEDIUM':
            threat_emoji = "🟠 *Medium Threat*"
        else:
            threat_emoji = "🟢 *Low Threat*"
            
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{comp_name}* | {threat_emoji}\n_{insight.executive_summary}_"
            }
        })
        
        # Build What Changed text
        changed_text = "\n".join([f"• *{x.category}:* {x.description}" for x in insight.what_changed])
        means_text = "\n".join([f"• *{x.category}:* {x.description}" for x in insight.what_it_means])
        todo_text = "\n".join([f"• *{x.category}:* {x.description}" for x in insight.what_to_do])
        
        if changed_text or means_text or todo_text:
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*What Changed:*\n{changed_text if changed_text else 'None'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*What It Means:*\n{means_text if means_text else 'None'}"
                    }
                ]
            })
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*What To Do:*\n{todo_text if todo_text else 'None'}"
                }
            })
            
        blocks.append({"type": "divider"})

    try:
        response = webhook.send(
            text=f"Weekly Briefing for {client_name}", 
            blocks=blocks
        )
        if response.status_code == 200:
            logger.info("Successfully delivered Slack briefing", client_name=client_name)
            return True
        else:
            logger.error("Slack webhook returned non-200 status", status_code=response.status_code, body=response.body)
            return False
    except Exception as e:
        logger.error("Failed to send Slack briefing", error=str(e))
        return False
