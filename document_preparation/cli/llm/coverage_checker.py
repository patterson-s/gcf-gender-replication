import anthropic
import json
import time
from typing import Dict, Any
from .prompts import COVERAGE_PROMPT

class CoverageCheckError(Exception):
    pass

def check_coverage(
    structure: Dict[str, Any],
    content: str,
    api_key: str,
    model: str,
    max_tokens: int,
    retry_attempts: int = 2
) -> Dict[str, Any]:
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise CoverageCheckError("Valid API key required")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    structure_text = ' '.join(structure.get('pages', []))
    prompt = COVERAGE_PROMPT.format(
        structure_text=structure_text,
        content=content
    )
    
    last_error = None
    for attempt in range(retry_attempts + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            raw = response.content[0].text
            start = raw.find('{')
            end = raw.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = raw[start:end]
                data = json.loads(json_str)
                return data
            else:
                return {"score": None, "text": raw}
                
        except anthropic.APIError as e:
            last_error = f"Claude API error: {str(e)}"
            if attempt < retry_attempts:
                time.sleep(2 ** attempt)
            continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            if attempt < retry_attempts:
                time.sleep(2 ** attempt)
            continue
    
    raise CoverageCheckError(f"Failed after {retry_attempts + 1} attempts. Last error: {last_error}")
