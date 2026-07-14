from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.client import Client
from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate, CompetitorResponse

router = APIRouter(prefix="/competitors", tags=["competitors"])

@router.post("/", response_model=CompetitorResponse, status_code=201)
def create_competitor(competitor_in: CompetitorCreate, db: Session = Depends(get_db)):
    # Ensure client exists
    client = db.query(Client).filter(Client.id == competitor_in.client_id).first()
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client_id. Client does not exist.")
        
    new_competitor = Competitor(**competitor_in.model_dump(exclude={'website_url'}))
    new_competitor.website_url = str(competitor_in.website_url)
    
    db.add(new_competitor)
    db.commit()
    db.refresh(new_competitor)
    return new_competitor

@router.get("/", response_model=List[CompetitorResponse])
def get_competitors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Competitor).offset(skip).limit(limit).all()

@router.get("/{competitor_id}", response_model=CompetitorResponse)
def get_competitor(competitor_id: int, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found.")
    return competitor

@router.put("/{competitor_id}", response_model=CompetitorResponse)
def update_competitor(competitor_id: int, competitor_in: CompetitorUpdate, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found.")
        
    update_data = competitor_in.model_dump(exclude_unset=True)
    if 'website_url' in update_data:
        update_data['website_url'] = str(update_data['website_url'])
        
    for key, value in update_data.items():
        setattr(competitor, key, value)
        
    db.commit()
    db.refresh(competitor)
    return competitor

@router.delete("/{competitor_id}", status_code=204)
def delete_competitor(competitor_id: int, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found.")
    db.delete(competitor)
    db.commit()
    return None
