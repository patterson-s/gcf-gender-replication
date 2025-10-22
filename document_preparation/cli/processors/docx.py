from typing import Tuple, Dict, Any
import os
from .base import BaseDocumentProcessor
from .utils import simple_token_count, normalize_structure

try:
    import docx
except ImportError:
    docx = None

class DOCXDocumentProcessor(BaseDocumentProcessor):
    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any], Dict[str, Any], bool]:
        text = ""
        structure = {"sections": []}
        
        if docx:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                structure["sections"].append(para.text)
                text += para.text + "\n"
        else:
            text = "[python-docx not installed]"
            structure["sections"].append(text)
        
        file_stats = os.stat(file_path)
        file_profile = {
            'size': file_stats.st_size,
            'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'filename': os.path.basename(file_path),
        }
        return text, normalize_structure(structure), file_profile, False

    def calculate_token_count(self, text: str) -> int:
        return simple_token_count(text)

    def prepare_for_processing(self, text: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "whole_document": text,
            "rag_chunks": structure.get("sections", [])
        }
