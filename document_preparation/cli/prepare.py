import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.processors.pdf import PDFDocumentProcessor
from cli.processors.docx import DOCXDocumentProcessor
from cli.processors.text import TextDocumentProcessor
from cli.llm.claude_extractor import extract_with_claude, ExtractionError
from cli.llm.coverage_checker import check_coverage, CoverageCheckError
from cli.output.writer import OutputWriter

def load_env_file(env_path: str = '.env'):
    if not os.path.exists(env_path):
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def get_api_key(config: dict) -> str:
    api_key = os.environ.get('CLAUDE_API_KEY')
    
    if not api_key:
        api_key = config.get('claude_api_key')
    
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        raise ValueError(
            "API key not found. Please either:\n"
            "  1. Set CLAUDE_API_KEY in .env file, or\n"
            "  2. Set CLAUDE_API_KEY environment variable, or\n"
            "  3. Set claude_api_key in config.json"
        )
    
    return api_key

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return json.load(f)

def detect_processor(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == '.pdf':
        return PDFDocumentProcessor()
    elif ext == '.docx':
        return DOCXDocumentProcessor()
    elif ext == '.txt':
        return TextDocumentProcessor()
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def main():
    parser = argparse.ArgumentParser(description='Extract text and metadata from documents')
    parser.add_argument('input_file', help='Input file path (PDF, DOCX, or TXT)')
    parser.add_argument('output_dir', help='Output directory path')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--no-coverage', action='store_true', help='Skip coverage check')
    parser.add_argument('--include-year', action='store_true', help='Extract year from document')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    if not os.path.exists(args.config):
        print(f"Error: Config file not found: {args.config}")
        print("Run: cp config.json.example config.json")
        sys.exit(1)
    
    load_env_file()
    
    try:
        config = load_config(args.config)
        api_key = get_api_key(config)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    filename = os.path.basename(args.input_file)
    writer = OutputWriter(args.output_dir, filename)
    writer.setup()
    
    try:
        writer.log(f"Detected file type: {Path(args.input_file).suffix}")
        processor = detect_processor(args.input_file)
        
        writer.log("Extracting text from document...")
        text, structure, file_profile, needs_ocr = processor.extract_text(args.input_file)
        
        if needs_ocr:
            writer.log("WARNING: Document may need OCR")
        
        page_count = len(structure.get('pages', structure.get('sections', [text])))
        token_count = processor.calculate_token_count(text)
        writer.log(f"Extracted {page_count} pages/sections, {token_count} tokens")
        
        writer.log("Calling Claude API for enhanced extraction...")
        try:
            first_page = structure.get('pages', [text])[0] if structure.get('pages') else text[:2000]
            
            llm_data, processing_ms = extract_with_claude(
                text=text,
                first_page_text=first_page,
                api_key=api_key,
                model=config['claude_model'],
                max_tokens=config['claude_max_tokens'],
                include_year=args.include_year,
                retry_attempts=config['retry_attempts']
            )
            
            writer.log(f"Claude extraction complete ({processing_ms}ms)")
            writer.log(f"Extracted metadata: title={llm_data.get('title')}, country={llm_data.get('country')}")
            
        except ExtractionError as e:
            writer.log(f"ERROR: LLM extraction failed: {e}")
            writer.log("Continuing with partial data...")
            llm_data = {
                'llm_markdown': text,
                'title': filename,
                'country': None,
                'region': None,
                'partner_name': None
            }
            processing_ms = 0
        
        coverage_score = None
        coverage_detail = None
        
        if not args.no_coverage and config.get('check_coverage', True):
            writer.log("Running coverage check...")
            try:
                coverage_result = check_coverage(
                    structure=structure,
                    content=llm_data.get('llm_markdown', ''),
                    api_key=api_key,
                    model=config['claude_model'],
                    max_tokens=config['claude_max_tokens'],
                    retry_attempts=config['retry_attempts']
                )
                coverage_score = coverage_result.get('score')
                coverage_detail = coverage_result.get('text')
                writer.log(f"Coverage check complete: score={coverage_score}/100")
                if coverage_detail:
                    writer.log(f"Coverage detail: {coverage_detail}")
            except CoverageCheckError as e:
                writer.log(f"WARNING: Coverage check failed: {e}")
        
        document_data = {
            'filename': filename,
            'mime_type': file_profile['type'],
            'size_bytes': file_profile['size'],
            'page_count': page_count,
            'token_count': token_count,
            'needs_ocr': needs_ocr,
            'title': llm_data.get('title'),
            'country': llm_data.get('country'),
            'region': llm_data.get('region'),
            'partner_name': llm_data.get('partner_name'),
            'llm_markdown': llm_data.get('llm_markdown'),
            'processing_timestamp': datetime.now().isoformat(),
            'llm_processing_ms': processing_ms,
            'coverage_score': coverage_score,
            'coverage_detail': coverage_detail
        }
        
        if args.include_year:
            document_data['year'] = llm_data.get('year')
        
        chunks = []
        pages = structure.get('pages', structure.get('sections', []))
        for idx, page_text in enumerate(pages, 1):
            chunks.append({
                'chunk_id': idx,
                'text': page_text,
                'source': {'page': idx}
            })
        
        writer.log(f"Writing outputs to: {writer.doc_dir}")
        writer.write_document(document_data)
        writer.write_chunks(chunks)
        writer.finalize("SUCCESS")
        
        print(f"\nSuccess! Output written to: {writer.doc_dir}")
        
    except Exception as e:
        writer.log(f"ERROR: {str(e)}")
        writer.finalize("FAILED")
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()