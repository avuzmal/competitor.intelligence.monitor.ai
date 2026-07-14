from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional

class ApifyRunInput(BaseModel):
    """
    Input schema to trigger an Apify run.
    This can be customized per actor.
    """
    model_config = ConfigDict(extra='allow')
    
    # Common field example
    startUrls: Optional[list[Dict[str, str]]] = None

class DeltaResponse(BaseModel):
    """
    Response model for the ingestion endpoint showing the calculated delta.
    """
    competitor_id: int
    is_first_run: bool
    delta: Dict[str, Any]
