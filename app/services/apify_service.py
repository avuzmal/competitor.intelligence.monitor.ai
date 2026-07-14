import logging
from typing import Dict, Any
from apify_client import ApifyClient
from app.core.config import settings

logger = logging.getLogger(__name__)

def fetch_competitor_data(apify_actor_id: str, run_input: dict) -> dict:
    """
    Triggers an Apify actor and fetches the resulting dataset items.
    
    Args:
        apify_actor_id: The ID or name of the Apify actor to run.
        run_input: The input JSON object to pass to the actor.
        
    Returns:
        dict: A dictionary containing the scraped data. Typically wraps the dataset 
              items in a {"items": [...]} structure.
    """
    # Initialize the ApifyClient with your Apify API token
    if not settings.apify_api_token:
        logger.warning("No APIFY_API_TOKEN set in environment. Returning mock data or failing.")
        raise ValueError("APIFY_API_TOKEN is not configured.")

    client = ApifyClient(settings.apify_api_token)

    logger.info(f"Triggering Apify actor {apify_actor_id} with input: {run_input}")
    
    # Start the actor and wait for it to finish
    run = client.actor(apify_actor_id).call(run_input=run_input)
    
    # Fetch the results from the actor's default dataset
    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        logger.error("No default dataset ID returned from Apify run.")
        return {"items": []}

    logger.info(f"Apify run finished. Fetching dataset items from {dataset_id}")
    dataset_items = client.dataset(dataset_id).list_items().items
    
    # Wrap in a dict to represent the raw data
    return {"items": dataset_items}
