import json
from bs4 import BeautifulSoup

def sanitize_delta_for_llm(raw_delta: dict, char_limit: int = 15000) -> str:
    """
    Cleans the raw delta output by stripping HTML, flattening nested structures,
    and removing empty values to prepare it for LLM ingestion.
    """
    cleaned_dict = _clean_node(raw_delta)
    
    # Flatten the dict for more readable text blocks instead of raw nested JSON
    flattened_lines = []
    _flatten_dict("", cleaned_dict, flattened_lines)
    
    final_text = "\n".join(flattened_lines)
    
    if len(final_text) > char_limit:
        # Simplistic truncation for Phase 2. 
        # In a real app we might prioritize specific keywords before truncating.
        final_text = final_text[:char_limit] + "\n...[TRUNCATED DUE TO LENGTH]"
        
    return final_text

def _clean_node(node):
    """
    Recursively clean dictionary nodes: strip HTML from strings, ignore empty values.
    """
    if isinstance(node, dict):
        cleaned = {}
        for k, v in node.items():
            if v is None or v == "" or v == [] or v == {}:
                continue
            cleaned_val = _clean_node(v)
            if cleaned_val:
                cleaned[k] = cleaned_val
        return cleaned
    elif isinstance(node, list):
        cleaned = []
        for item in node:
            if item is None or item == "" or item == [] or item == {}:
                continue
            cleaned_val = _clean_node(item)
            if cleaned_val:
                cleaned.append(cleaned_val)
        return cleaned
    elif isinstance(node, str):
        # Strip HTML using BeautifulSoup
        soup = BeautifulSoup(node, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text if text else None
    else:
        return node

def _flatten_dict(prefix: str, d: dict, lines: list):
    """
    Convert a dictionary into flattened lines: e.g. "Root -> Key -> Value: Result"
    """
    if isinstance(d, dict):
        for k, v in d.items():
            new_prefix = f"{prefix} -> {k}" if prefix else str(k)
            if isinstance(v, (dict, list)):
                _flatten_dict(new_prefix, v, lines)
            else:
                lines.append(f"{new_prefix}: {v}")
    elif isinstance(d, list):
        for i, item in enumerate(d):
            new_prefix = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)):
                _flatten_dict(new_prefix, item, lines)
            else:
                lines.append(f"{new_prefix}: {item}")
