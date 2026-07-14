import pytest
from app.services.delta_engine import calculate_delta
from app.services.data_sanitizer import sanitize_delta_for_llm, _clean_node, _flatten_dict
from app.models.snapshot import Snapshot
from unittest.mock import MagicMock

def test_sanitize_delta_for_llm_strips_html():
    raw = {"data": "<p>Hello <b>World</b></p>"}
    result = sanitize_delta_for_llm(raw)
    assert result == "data: Hello World"

def test_sanitize_delta_for_llm_removes_empty():
    raw = {"valid": "data", "empty_str": "", "empty_dict": {}, "empty_list": [], "none_val": None}
    result = sanitize_delta_for_llm(raw)
    assert result == "valid: data"
    assert "empty" not in result

def test_sanitize_delta_for_llm_truncates():
    raw = {"data": "A" * 20000}
    result = sanitize_delta_for_llm(raw, char_limit=100)
    assert len(result) <= 100 + len("\n...[TRUNCATED DUE TO LENGTH]")
    assert "...[TRUNCATED DUE TO LENGTH]" in result

def test_sanitize_delta_for_llm_flattening():
    raw = {"level1": {"level2": {"level3": "value"}}, "list": ["a", "b"]}
    result = sanitize_delta_for_llm(raw)
    assert "level1 -> level2 -> level3: value" in result
    assert "list[0]: a" in result
    assert "list[1]: b" in result

def test_calculate_delta_first_run():
    session = MagicMock()
    # No previous snapshot
    session.query().filter().order_by().first.return_value = None
    
    new_data = {"key": "value"}
    delta = calculate_delta(1, new_data, session)
    
    assert delta["added_items"] == new_data
    assert delta["removed_items"] == {}
    assert delta["modified_items"] == {}

def test_calculate_delta_with_snapshot():
    session = MagicMock()
    mock_snapshot = MagicMock(spec=Snapshot)
    mock_snapshot.id = 1
    mock_snapshot.raw_data = {"old_key": "old_value", "shared": "same"}
    session.query().filter().order_by().first.return_value = mock_snapshot
    
    new_data = {"new_key": "new_value", "shared": "same"}
    delta = calculate_delta(1, new_data, session)
    
    # DeepDiff stores results in specific formats
    assert "dictionary_item_added" in delta["added_items"] or str(delta["added_items"]) != "{}"
    assert "dictionary_item_removed" in delta["removed_items"] or str(delta["removed_items"]) != "{}"
    assert "new_key" in str(delta["added_items"])
    assert "old_key" in str(delta["removed_items"])
