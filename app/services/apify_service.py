import logging
from typing import Dict, Any
from apify_client import ApifyClient
from app.core.config import settings
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = structlog.get_logger(__name__)

class ApifyScrapeError(Exception):
    """Exception raised for errors during Apify scraping."""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def _call_apify(actor_id: str, run_input: dict) -> dict:
    if not settings.apify_api_token:
        raise ValueError("APIFY_API_TOKEN is not configured.")
        
    client = ApifyClient(settings.apify_api_token)
    logger.info("Calling Apify actor", actor_id=actor_id)
    run = client.actor(actor_id).call(run_input=run_input)
    
    if run is None or run.get("defaultDatasetId") is None:
        raise ApifyScrapeError(f"Failed to run Apify actor {actor_id}")
        
    logger.info("Fetching Apify dataset", dataset_id=run["defaultDatasetId"])
    dataset = client.dataset(run["defaultDatasetId"]).list_items().items
    return {"items": dataset}

def fetch_competitor_data(apify_actor_id: str, run_input: dict) -> dict:
    """
    Triggers an Apify Actor with the specified input and waits for the results.
    
    Args:
        apify_actor_id (str): The ID of the Apify Actor to run.
        run_input (dict): The input payload for the Actor.
        
    Returns:
        dict: A dictionary containing the scraped data. Typically wraps the dataset 
              items in a {"items": [...]} structure.
    """
    try:
        return _call_apify(apify_actor_id, run_input)
    except Exception as e:
        logger.error("Apify scraping failed completely after retries", actor_id=apify_actor_id, error=str(e))
        return {"items": []}
