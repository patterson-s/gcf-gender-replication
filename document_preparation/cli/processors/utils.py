import re
from typing import Dict, Any

def simple_token_count(text: str) -> int:
    return len(re.findall(r'\w+', text))

def normalize_structure(structure: Dict[str, Any]) -> Dict[str, Any]:
    return structure
