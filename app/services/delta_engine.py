import json
import logging
from typing import Dict, Any
from deepdiff import DeepDiff
from sqlalchemy.orm import Session
from app.models.snapshot import Snapshot

logger = logging.getLogger(__name__)

def calculate_delta(competitor_id: int, new_raw_data: dict, db_session: Session) -> dict:
    """
    Calculates the delta between new_raw_data and the most recent snapshot.

    Args:
        competitor_id: ID of the competitor being processed.
        new_raw_data: The fresh scraped data dictionary.
        db_session: SQLAlchemy session.

    Returns:
        dict: A dictionary containing 'added_items', 'removed_items', and 'modified_items'.
              If it's the first run, the dictionary represents all new_raw_data under 'added_items'.
    """
    # Fetch the most recent snapshot for this competitor
    previous_snapshot = (
        db_session.query(Snapshot)
        .filter(Snapshot.competitor_id == competitor_id)
        .order_by(Snapshot.scrape_date.desc())
        .first()
    )

    if not previous_snapshot:
        logger.info(f"No previous snapshot found for competitor {competitor_id}. This is the first run.")
        return {
            "added_items": new_raw_data,
            "removed_items": {},
            "modified_items": {}
        }

    logger.info(f"Comparing new data against snapshot ID {previous_snapshot.id}")
    old_raw_data = previous_snapshot.raw_data

    # Use DeepDiff to perform a robust JSON diffing mechanism
    # ignore_order=True handles lists where item order changed but content is same
    diff = DeepDiff(old_raw_data, new_raw_data, ignore_order=True, report_repetition=True)

    delta = {
        "added_items": _parse_deepdiff_result(diff, 'dictionary_item_added', 'iterable_item_added'),
        "removed_items": _parse_deepdiff_result(diff, 'dictionary_item_removed', 'iterable_item_removed'),
        "modified_items": _parse_deepdiff_result(diff, 'values_changed', 'type_changes')
    }

    return delta


def _parse_deepdiff_result(diff: DeepDiff, *keys: str) -> dict:
    """
    Helper function to extract and combine specific diff categories from DeepDiff result.
    Converts complex objects back into a simpler dictionary representation.
    """
    result = {}
    for key in keys:
        if key in diff:
            # DeepDiff returns PrettyOrderedSet for some keys, convert to dict/list
            if isinstance(diff[key], dict):
                result.update(diff[key])
            else:
                result[key] = list(diff[key])
    
    # We parse the output to standard JSON-serializable formats
    # For a full production implementation, we might parse the root.items[0] string 
    # to a proper structured dict. For Phase 1, DeepDiff's format string or dictionary is fine.
    
    # Deepdiff uses custom objects (like standard python sets, or Tree objects), so we JSON serialize
    # it to clean it up via DeepDiff's to_json utility if needed, but dict conversion works for simple cases.
    return json.loads(diff.to_json()).get(keys[0], {}) if keys and keys[0] in json.loads(diff.to_json()) else result
