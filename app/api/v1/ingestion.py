from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.competitor import Competitor
from app.models.snapshot import Snapshot
from app.schemas.apify import ApifyRunInput, DeltaResponse
from app.services.apify_service import fetch_competitor_data
from app.services.delta_engine import calculate_delta

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("/{competitor_id}", response_model=DeltaResponse)
def ingest_competitor_data(
    competitor_id: int, 
    run_input: ApifyRunInput, 
    db: Session = Depends(get_db)
):
    """
    Trigger Apify scrape for a specific competitor, calculate the data delta 
    against the previous week, and save the fresh state snapshot.
    """
    # 1. Verify Competitor exists
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found.")

    # 2. Fetch data from Apify
    try:
        new_raw_data = fetch_competitor_data(
            apify_actor_id=competitor.apify_actor_id,
            run_input=run_input.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from Apify: {str(e)}")

    # 3. Calculate Delta against the latest snapshot in the DB
    try:
        # Determine if it's the first run to pass correctly to the response
        previous_snapshot = db.query(Snapshot).filter(Snapshot.competitor_id == competitor_id).first()
        is_first_run = previous_snapshot is None

        delta = calculate_delta(
            competitor_id=competitor_id,
            new_raw_data=new_raw_data,
            db_session=db
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate delta: {str(e)}")

    # 4. Save new snapshot
    try:
        new_snapshot = Snapshot(
            competitor_id=competitor_id,
            raw_data=new_raw_data,
            scrape_date=datetime.utcnow()
        )
        db.add(new_snapshot)
        db.commit()
        db.refresh(new_snapshot)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save new snapshot: {str(e)}")

    # 5. Return the calculated delta
    return DeltaResponse(
        competitor_id=competitor_id,
        is_first_run=is_first_run,
        delta=delta
    )
