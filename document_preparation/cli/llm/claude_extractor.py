import anthropic
import json
import time
from typing import Dict, Any, Tuple
from .prompts import EXTRACTION_PROMPT_BASE, EXTRACTION_PROMPT_WITH_YEAR

class ExtractionError(Exception):
    pass

def parse_llm_json(data: str) -> Dict[str, Any]:
    import re
    try:
        return json.loads(data)
    except Exception:
        pass
    
    data_stripped = data.strip()
    if data_stripped.startswith('```'):
        data_stripped = re.sub(r'^```[a-zA-Z]*\n', '', data_stripped)
        if data_stripped.endswith('```'):
            data_stripped = re.sub(r'```$', '', data_stripped)
        data_stripped = data_stripped.strip()
        try:
            return json.loads(data_stripped)
        except Exception:
            pass
    
    try:
        match = re.search(r'\{[\s\S]*\}', data)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass
    
    raise ExtractionError(f"Failed to parse JSON from response: {data[:200]}")

def extract_with_claude(
    text: str,
    first_page_text: str,
    api_key: str,
    model: str,
    max_tokens: int,
    include_year: bool = False,
    retry_attempts: int = 2
) -> Tuple[Dict[str, Any], int]:
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise ExtractionError("Valid API key required")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt_template = EXTRACTION_PROMPT_WITH_YEAR if include_year else EXTRACTION_PROMPT_BASE
    full_prompt = prompt_template.format(
        first_page_text=first_page_text,
        full_text=text
    )
    
    last_error = None
    for attempt in range(retry_attempts + 1):
        try:
            start_time = time.time()
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0,
                messages=[{"role": "user", "content": full_prompt}]
            )
            processing_ms = int((time.time() - start_time) * 1000)
            
            raw = response.content[0].text
            data = parse_llm_json(raw)
            return data, processing_ms
            
        except anthropic.APIError as e:
            last_error = f"Claude API error: {str(e)}"
            if attempt < retry_attempts:
                time.sleep(2 ** attempt)
            continue
        except ExtractionError as e:
            last_error = str(e)
            if attempt < retry_attempts:
                time.sleep(2 ** attempt)
            continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            if attempt < retry_attempts:
                time.sleep(2 ** attempt)
            continue
    
    raise ExtractionError(f"Failed after {retry_attempts + 1} attempts. Last error: {last_error}")
