from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

class BaseDocumentProcessor(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any], Dict[str, Any], bool]:
        pass

    @abstractmethod
    def calculate_token_count(self, text: str) -> int:
        pass

    @abstractmethod
    def prepare_for_processing(self, text: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        pass
