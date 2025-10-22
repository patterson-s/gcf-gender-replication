from typing import Tuple, Dict, Any
import os
from .base import BaseDocumentProcessor
from .utils import simple_token_count, normalize_structure

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

class PDFDocumentProcessor(BaseDocumentProcessor):
    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any], Dict[str, Any], bool]:
        text = ""
        structure = {"pages": []}
        needs_ocr = False
        
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text() or ""
                        structure["pages"].append(page_text)
                        text += page_text + "\n"
                if not text.strip():
                    needs_ocr = True
            except Exception as e:
                print(f"[DEBUG] Exception in pdfplumber.open: {e}")
                needs_ocr = True
        else:
            needs_ocr = True
        
        file_stats = os.stat(file_path)
        file_profile = {
            'size': file_stats.st_size,
            'type': 'application/pdf',
            'filename': os.path.basename(file_path),
        }
        return text, normalize_structure(structure), file_profile, needs_ocr

    def calculate_token_count(self, text: str) -> int:
        return simple_token_count(text)

    def prepare_for_processing(self, text: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "whole_document": text,
            "rag_chunks": structure.get("pages", [])
        }
