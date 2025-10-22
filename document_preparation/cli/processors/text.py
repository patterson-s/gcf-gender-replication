from typing import Tuple, Dict, Any
import os
from .base import BaseDocumentProcessor
from .utils import simple_token_count, normalize_structure

class TextDocumentProcessor(BaseDocumentProcessor):
    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any], Dict[str, Any], bool]:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        structure = {"full_text": text}
        
        file_stats = os.stat(file_path)
        file_profile = {
            'size': file_stats.st_size,
            'type': 'text/plain',
            'filename': os.path.basename(file_path),
        }
        return text, normalize_structure(structure), file_profile, False

    def calculate_token_count(self, text: str) -> int:
        return simple_token_count(text)

    def prepare_for_processing(self, text: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "whole_document": text,
            "rag_chunks": [text]
        }
