EXTRACTION_PROMPT_BASE = """
Below is the full text of the PDF. Please:
1. Extract all text and tables from the PDF and return the entire content as Markdown (llm_markdown), preserving structure and formatting as much as possible.
2. Extract the document title (from the first page).
3. Extract the geographic country or countries (from the first page). if there are multiple countries, return a list of countries in a string.
4. Identify the geographic region based on the country(s). If there are multiple regions, return 'multiple'
5. Extract the Partner Name (from the first page, found between two '|' characters, e.g., | MUFG Bank | = MUFG Bank).

Return ONLY a single, properly formatted JSON object with the following keys, and do not include any introduction, explanation, code block, or follow-up text. The response MUST be valid JSON and nothing else:
- llm_markdown (string)
- title (string)
- country (string)
- region (string)
- partner_name (string)

Example:
{{
  "llm_markdown": "...",
  "title": "...",
  "country": "...",
  "region": "...",
  "partner_name": "..."
}}

Here is the PDF text:
{first_page_text}

{full_text}
"""

EXTRACTION_PROMPT_WITH_YEAR = """
Below is the full text of the PDF. Please:
1. Extract all text and tables from the PDF and return the entire content as Markdown (llm_markdown), preserving structure and formatting as much as possible.
2. Extract the document title (from the first page).
3. Extract the geographic country or countries (from the first page). if there are multiple countries, return a list of countries in a string.
4. Identify the geographic region based on the country(s). If there are multiple regions, return 'multiple'
5. Extract the Partner Name (from the first page, found between two '|' characters, e.g., | MUFG Bank | = MUFG Bank).
6. Extract the year of the report.

Return ONLY a single, properly formatted JSON object with the following keys, and do not include any introduction, explanation, code block, or follow-up text. The response MUST be valid JSON and nothing else:
- llm_markdown (string)
- title (string)
- country (string)
- region (string)
- partner_name (string)
- year (string)

Example:
{{
  "llm_markdown": "...",
  "title": "...",
  "country": "...",
  "region": "...",
  "partner_name": "...",
  "year": "2023"
}}

Here is the PDF text:
{first_page_text}

{full_text}
"""

COVERAGE_PROMPT = """You are an expert at document comparison. Below are two texts:
Source PDF: (raw extracted text)
{structure_text}

Extracted Text: (LLM Markdown output)
{content}

What percentage of the information in the Source PDF is present in the Extracted Text? Evaluate only the text content, not the formatting. Respond ONLY with a JSON object in this format: {{"score": <integer between 0 and 100>, "text": "<short explanation blurb beginning with: The Extracted Text ... >"}}"""
