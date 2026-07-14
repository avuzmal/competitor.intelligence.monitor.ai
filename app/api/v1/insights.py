import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from deepdiff import DeepDiff

from app.core.database import get_db
from app.models.competitor import Competitor
from app.models.snapshot import Snapshot
from app.schemas.insights import CompetitorInsight
from app.services.data_sanitizer import sanitize_delta_for_llm
from app.services.claude_service import generate_strategic_insights

router = APIRouter(prefix="/insights", tags=["insights"])

def _parse_diff(diff_obj: DeepDiff, *keys: str) -> dict:
    """Helper to parse DeepDiff objects similar to delta_engine."""
    res = {}
    for k in keys:
        if k in diff_obj:
            if isinstance(diff_obj[k], dict):
                res.update(diff_obj[k])
            else:
                res[k] = list(diff_obj[k])
    
    parsed_json = json.loads(diff_obj.to_json())
    return parsed_json.get(keys[0], {}) if keys and keys[0] in parsed_json else res

@router.post("/generate/{competitor_id}", response_model=CompetitorInsight)
def generate_insights_for_competitor(
    competitor_id: int, 
    db: Session = Depends(get_db)
):
    # 1. Fetch Competitor and Snapshots
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found.")
        
    snapshots = db.query(Snapshot).filter(Snapshot.competitor_id == competitor_id).order_by(Snapshot.scrape_date.desc()).limit(2).all()
    
    if not snapshots:
        raise HTTPException(status_code=400, detail="No snapshots found for this competitor. Ingest data first.")
        
    # 2. Calculate the delta
    if len(snapshots) < 2:
        # First run, the entire snapshot is the delta
        raw_delta = {
            "added_items": snapshots[0].raw_data,
            "removed_items": {},
            "modified_items": {}
        }
    else:
        new_data = snapshots[0].raw_data
        old_data = snapshots[1].raw_data
        
        diff = DeepDiff(old_data, new_data, ignore_order=True, report_repetition=True)
        raw_delta = {
            "added_items": _parse_diff(diff, 'dictionary_item_added', 'iterable_item_added'),
            "removed_items": _parse_diff(diff, 'dictionary_item_removed', 'iterable_item_removed'),
            "modified_items": _parse_diff(diff, 'values_changed', 'type_changes')
        }
        
    # Check if delta is empty
    is_empty = not raw_delta.get("added_items") and not raw_delta.get("removed_items") and not raw_delta.get("modified_items")
    
    if is_empty:
        return CompetitorInsight(
            executive_summary="No changes detected.",
            what_changed=[],
            what_it_means=[],
            what_to_do=[],
            threat_level="LOW"
        )
        
    # 3. Sanitize
    sanitized_text = sanitize_delta_for_llm(raw_delta)
    
    # 4. Generate insights via Claude
    insights = generate_strategic_insights(
        competitor_name=competitor.name, 
        sanitized_delta=sanitized_text
    )
    
    return insights
