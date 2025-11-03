"""
llama.cpp adapter for GGUF models
"""
from typing import Dict, Any, Generator
from app.adapters import ModelAdapter
import logging

logger = logging.getLogger(__name__)


class LlamaCppAdapter(ModelAdapter):
    """Adapter for llama.cpp GGUF models"""
    
    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.model = None
        
    def load(self) -> None:
        """Load GGUF model using llama-cpp-python"""
        try:
            from llama_cpp import Llama
            
            weights_path = self.manifest["files"]["weights"]
            defaults = self.manifest.get("defaults", {})
            
            logger.info(f"Loading llama.cpp model from {weights_path}")
            
            self.model = Llama(
                model_path=weights_path,
                n_ctx=self.manifest.get("context_length", 2048),
                n_threads=defaults.get("threads", 2),
                n_gpu_layers=0,  # CPU-only by default
                verbose=False
            )
            
            self.loaded = True
            logger.info(f"Successfully loaded model {self.manifest['id']}")
            
        except Exception as e:
            logger.error(f"Failed to load llama.cpp model: {e}")
            raise
    
    def unload(self) -> None:
        """Unload the model"""
        if self.model:
            del self.model
            self.model = None
            self.loaded = False
            logger.info(f"Unloaded model {self.manifest['id']}")
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """Tokenize text"""
        if not self.loaded or not self.model:
            raise RuntimeError("Model not loaded")
        
        tokens = self.model.tokenize(text.encode('utf-8'))
        
        return {
            "tokens": [self.model.detokenize([t]).decode('utf-8', errors='ignore') for t in tokens],
            "ids": tokens,
            "count": len(tokens)
        }
    
    def generate(self, request: Dict[str, Any]) -> Generator[str, None, None]:
        """Generate text with streaming"""
        if not self.loaded or not self.model:
            raise RuntimeError("Model not loaded")
        
        # Extract parameters
        prompt = request.get("prompt", "")
        messages = request.get("messages")
        
        # Format prompt if messages provided
        if messages:
            prompt = self._format_messages(messages)
        
        temperature = request.get("temperature", self.manifest.get("defaults", {}).get("temperature", 0.7))
        top_p = request.get("top_p", self.manifest.get("defaults", {}).get("top_p", 0.9))
        max_tokens = request.get("max_tokens", self.manifest.get("defaults", {}).get("max_tokens", 256))
        stop = request.get("stop", [])
        
        # Add template stop tokens if available
        if self.manifest.get("prompt_template", {}).get("stop"):
            stop.extend(self.manifest["prompt_template"]["stop"])
        
        try:
            # Stream generation
            for output in self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop if stop else None,
                stream=True,
                echo=False
            ):
                if "choices" in output and len(output["choices"]) > 0:
                    token = output["choices"][0].get("text", "")
                    if token:
                        yield token
                        
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    def _format_messages(self, messages: list) -> str:
        """Format messages according to model's prompt template"""
        template = self.manifest.get("prompt_template", {})
        
        if template.get("chat"):
            # Use chat template if available
            formatted = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                formatted += template["chat"].format(role=role, content=content)
            return formatted
        else:
            # Simple concatenation
            return "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
