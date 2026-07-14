import os
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Any
from datetime import datetime
from app.schemas.insights import CompetitorInsight

# Setup Jinja2 environment pointing to the templates directory
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def render_briefing_email(client_name: str, insights_list: List[Dict[str, Any]]) -> str:
    """
    Renders the weekly briefing HTML email.
    
    Args:
        client_name: The name of the client receiving the email.
        insights_list: A list of dictionaries containing:
                       {"competitor_name": "...", "insight": CompetitorInsight}
    
    Returns:
        A formatted HTML string ready for emailing.
    """
    template = env.get_template("weekly_briefing.html")
    
    html_content = template.render(
        client_name=client_name,
        insights_list=insights_list,
        date_str=datetime.now().strftime("%B %d, %Y"),
        year=datetime.now().year
    )
    
    return html_content
