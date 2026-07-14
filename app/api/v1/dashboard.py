from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Annotated
import structlog
from pydantic import BaseModel, HttpUrl
from datetime import datetime

from app.core.database import get_db
from app.models.client import Client
from app.models.competitor import Competitor
from app.models.briefing_history import BriefingHistory
from app.schemas.competitor import CompetitorResponse, CompetitorCreate

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class BriefingHistoryResponse(BaseModel):
    id: int
    competitor_id: int
    scrape_date: datetime
    insight_json: dict
    delivery_status: str
    
    model_config = {"from_attributes": True}

async def verify_client_ownership(
    x_client_id: Annotated[int, Header()],
    db: Session = Depends(get_db)
) -> Client:
    """
    Validates that the provided X-Client-Id header corresponds to a valid Client.
    """
    client = db.query(Client).filter(Client.id == x_client_id).first()
    if not client:
        raise HTTPException(status_code=401, detail="Unauthorized client access")
    return client

@router.get("/briefings", response_model=List[BriefingHistoryResponse])
def get_client_briefings(
    skip: int = 0, 
    limit: int = 50,
    client: Client = Depends(verify_client_ownership),
    db: Session = Depends(get_db)
):
    """
    Returns a paginated list of past briefings for the authenticated client.
    """
    briefings = (
        db.query(BriefingHistory)
        .filter(BriefingHistory.client_id == client.id)
        .order_by(BriefingHistory.scrape_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return briefings

@router.post("/competitors", response_model=CompetitorResponse, status_code=201)
def add_competitor(
    competitor_in: CompetitorCreate,
    client: Client = Depends(verify_client_ownership),
    db: Session = Depends(get_db)
):
    """
    Adds a new competitor for the authenticated client.
    """
    if competitor_in.client_id != client.id:
        raise HTTPException(status_code=403, detail="Cannot add competitor for another client.")
        
    new_competitor = Competitor(**competitor_in.model_dump(exclude={'website_url'}))
    new_competitor.website_url = str(competitor_in.website_url)
    
    db.add(new_competitor)
    db.commit()
    db.refresh(new_competitor)
    return new_competitor

@router.delete("/competitors/{competitor_id}", status_code=204)
def remove_competitor(
    competitor_id: int,
    client: Client = Depends(verify_client_ownership),
    db: Session = Depends(get_db)
):
    """
    Stops tracking a competitor for the authenticated client.
    """
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id, Competitor.client_id == client.id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found or not owned by client.")
        
    db.delete(competitor)
    db.commit()
    return None
