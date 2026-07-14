import logging
from anthropic import Anthropic, APIError
from app.core.config import settings
from app.schemas.insights import CompetitorInsight

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an elite Competitive Intelligence Strategist. Your job is to analyze weekly changes in a competitor's business and translate them into actionable strategy for your client.
RULES:
NO GENERIC ADVICE. Do not say 'improve marketing' or 'monitor closely'. Every recommendation must be a direct, specific response to the data provided.
READ BETWEEN THE LINES. If they post 3 iOS developer jobs, the signal is 'mobile launch in 90 days'. If they drop prices by 20%, the signal is 'desperate for market share or responding to our new feature'.
BE RUTHLESSLY OBJECTIVE. If the changes are trivial (e.g., they changed a footer copyright year), state clearly that there are no significant strategic shifts. Do not invent drama.
FORMAT STRICTLY. You must output valid JSON matching the provided schema."""

def generate_strategic_insights(competitor_name: str, sanitized_delta: str) -> CompetitorInsight:
    if not settings.anthropic_api_key:
        logger.error("Anthropic API key is missing.")
        return CompetitorInsight(
            executive_summary="API Key missing. Cannot generate insights.",
            what_changed=[],
            what_it_means=[],
            what_to_do=[],
            threat_level="LOW"
        )
        
    client = Anthropic(api_key=settings.anthropic_api_key)
    
    # Use Anthropic's tool-use feature to enforce the Pydantic schema
    schema = CompetitorInsight.model_json_schema()
    # Pydantic JSON schema sometimes includes $defs, which Anthropic doesn't natively support 
    # at the root level of tool inputs. However, Anthropic's strict JSON mode works well.
    # We wrap it correctly:
    
    tools = [
        {
            "name": "record_competitor_insights",
            "description": "Records the final strategic insights derived from the data.",
            "input_schema": schema
        }
    ]
    
    user_prompt = f"Analyze the following changes for competitor: {competitor_name}\n\nDATA:\n{sanitized_delta}"
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            tools=tools,
            tool_choice={"type": "tool", "name": "record_competitor_insights"}
        )
        
        # Find the tool use block
        for block in response.content:
            if block.type == "tool_use" and block.name == "record_competitor_insights":
                return CompetitorInsight(**block.input)
                
        logger.error("Claude did not return a tool_use block.")
        raise ValueError("Invalid response format from Claude.")
        
    except APIError as e:
        logger.error(f"Anthropic API Error: {e}")
        return CompetitorInsight(
            executive_summary=f"Anthropic API Error occurred: {e}",
            what_changed=[],
            what_it_means=[],
            what_to_do=[],
            threat_level="LOW"
        )
    except Exception as e:
        logger.error(f"Error parsing Claude response: {e}")
        return CompetitorInsight(
            executive_summary=f"Parsing Error occurred: {e}",
            what_changed=[],
            what_it_means=[],
            what_to_do=[],
            threat_level="LOW"
        )
