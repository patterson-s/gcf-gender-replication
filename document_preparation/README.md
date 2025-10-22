# Document Preparation CLI

Extracts text, metadata, and structure from PDF/DOCX/TXT files using Claude API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API key:
```bash
cp config.json.example config.json
# Edit config.json and replace YOUR_API_KEY_HERE with your Anthropic API key
```

## Usage

Basic usage:
```bash
python cli/prepare.py input.pdf output_dir/
```

Skip coverage check:
```bash
python cli/prepare.py input.pdf output_dir/ --no-coverage
```

Custom config:
```bash
python cli/prepare.py input.pdf output_dir/ --config custom-config.json
```

## Output Structure

For input file `fp025-gender-action-plan.pdf`:

```
output_dir/
  fp025-gender-action-plan/
    document.json      # Metadata + LLM extraction
    chunks.json        # Page-by-page content
    processing.log     # Quality control log
```

## Config Options

- `claude_api_key`: Your Anthropic API key
- `claude_model`: Model to use (default: claude-sonnet-4-20250514)
- `claude_max_tokens`: Max tokens per request (default: 8192)
- `retry_attempts`: Number of retries on failure (default: 2)
- `check_coverage`: Run coverage quality check (default: true)
