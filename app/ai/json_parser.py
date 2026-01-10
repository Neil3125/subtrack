"""Helper to extract and parse JSON from AI responses."""
import json
import re
from typing import Any, Optional


def extract_json_from_response(response: str) -> Optional[dict]:
    """
    Extract JSON from an AI response that might contain extra text.
    
    Handles cases where AI adds explanation text before/after the JSON.
    """
    # Try direct JSON parsing first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON in code blocks
    code_block_patterns = [
        r'```json\s*(.*?)\s*```',  # ```json ... ```
        r'```\s*(.*?)\s*```',       # ``` ... ```
    ]
    
    for pattern in code_block_patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON object directly in text
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Match nested JSON objects
    ]
    
    for pattern in json_patterns:
        matches = re.finditer(pattern, response, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                continue
    
    # If nothing works, return None
    return None


def safe_json_parse(response: str, fallback: dict) -> dict:
    """
    Safely parse JSON from AI response with fallback.
    
    Args:
        response: AI response that should contain JSON
        fallback: Default dict to return if parsing fails
        
    Returns:
        Parsed JSON dict or fallback dict
    """
    result = extract_json_from_response(response)
    return result if result is not None else fallback
