"""
Base adapter interface for model backends
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Generator, Optional


class ModelAdapter(ABC):
    """
    Abstract base class for model adapters.
    All adapters must implement this interface.
    """
    
    def __init__(self, manifest: Dict[str, Any]):
        """
        Initialize the adapter with a model manifest.
        
        Args:
            manifest: Model manifest dictionary
        """
        self.manifest = manifest
        self.loaded = False
    
    @abstractmethod
    def load(self) -> None:
        """Load the model into memory"""
        pass
    
    @abstractmethod
    def unload(self) -> None:
        """Unload the model from memory"""
        pass
    
    @abstractmethod
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize input text.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            Dictionary with 'tokens' (list) and 'ids' (list)
        """
        pass
    
    @abstractmethod
    def generate(self, request: Dict[str, Any]) -> Generator[str, None, None]:
        """
        Generate text with streaming support.
        
        Args:
            request: Generation request dictionary with:
                - prompt (str) or messages (list)
                - temperature (float)
                - top_p (float)
                - max_tokens (int)
                - stop (list)
                
        Yields:
            Generated tokens as strings
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "id": self.manifest.get("id"),
            "name": self.manifest.get("name"),
            "adapter": self.manifest.get("adapter"),
            "loaded": self.loaded,
            "context_length": self.manifest.get("context_length", 2048)
        }
