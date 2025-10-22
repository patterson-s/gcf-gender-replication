import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class OutputWriter:
    def __init__(self, output_dir: str, filename: str):
        self.output_dir = Path(output_dir)
        self.filename = filename
        self.doc_dir = self.output_dir / Path(filename).stem
        self.log_entries = []
        
    def setup(self):
        self.doc_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"Starting processing: {self.filename}")
        
    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.log_entries.append(entry)
        print(entry)
        
    def write_document(self, data: Dict[str, Any]):
        doc_path = self.doc_dir / "document.json"
        with open(doc_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.log(f"Wrote document.json")
        
    def write_chunks(self, chunks: List[Dict[str, Any]]):
        chunks_path = self.doc_dir / "chunks.json"
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump({"chunks": chunks}, f, indent=2, ensure_ascii=False)
        self.log(f"Wrote chunks.json with {len(chunks)} chunks")
        
    def write_log(self):
        log_path = self.doc_dir / "processing.log"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.log_entries))
        
    def finalize(self, status: str = "SUCCESS"):
        self.log(f"Processing complete: {status}")
        self.write_log()
