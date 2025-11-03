"""
Victor custom backend adapter
"""
from typing import Dict, Any, Generator
from app.adapters import ModelAdapter
import logging
import os
import sys
import importlib.util

logger = logging.getLogger(__name__)


class VictorCustomAdapter(ModelAdapter):
    """Adapter for custom Victor backend"""
    
    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.victor_module = None
        self.config = None
        
    def load(self) -> None:
        """Load Victor custom backend"""
        try:
            # Get Victor directory path
            victor_dir = self.manifest["files"].get("weights", "")
            
            if not os.path.isdir(victor_dir):
                raise ValueError(f"Victor directory not found: {victor_dir}")
            
            runner_path = os.path.join(victor_dir, "runner.py")
            config_path = os.path.join(victor_dir, "config.yaml")
            
            if not os.path.exists(runner_path):
                raise ValueError(f"Victor runner.py not found in {victor_dir}")
            
            logger.info(f"Loading Victor custom backend from {victor_dir}")
            
            # Load config if available
            if os.path.exists(config_path):
                import yaml
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = {}
            
            # Dynamically import runner module
            spec = importlib.util.spec_from_file_location("victor_runner", runner_path)
            if spec and spec.loader:
                self.victor_module = importlib.util.module_from_spec(spec)
                sys.modules["victor_runner"] = self.victor_module
                spec.loader.exec_module(self.victor_module)
            else:
                raise ImportError(f"Failed to load Victor runner from {runner_path}")
            
            # Initialize Victor backend
            if hasattr(self.victor_module, 'init'):
                self.victor_module.init(self.config)
            
            self.loaded = True
            logger.info(f"Successfully loaded Victor backend {self.manifest['id']}")
            
        except Exception as e:
            logger.error(f"Failed to load Victor backend: {e}")
            raise
    
    def unload(self) -> None:
        """Unload Victor backend"""
        if self.victor_module:
            # Call cleanup if available
            if hasattr(self.victor_module, 'cleanup'):
                try:
                    self.victor_module.cleanup()
                except:
                    pass
            
            # Remove from sys.modules
            if "victor_runner" in sys.modules:
                del sys.modules["victor_runner"]
            
            self.victor_module = None
        
        self.config = None
        self.loaded = False
        logger.info(f"Unloaded Victor backend {self.manifest['id']}")
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """Tokenize text using Victor backend"""
        if not self.loaded or not self.victor_module:
            raise RuntimeError("Victor backend not loaded")
        
        if hasattr(self.victor_module, 'tokenize'):
            try:
                result = self.victor_module.tokenize(text)
                return result
            except Exception as e:
                logger.error(f"Victor tokenization error: {e}")
        
        # Fallback
        tokens = text.split()
        return {
            "tokens": tokens,
            "ids": list(range(len(tokens))),
            "count": len(tokens)
        }
    
    def generate(self, request: Dict[str, Any]) -> Generator[str, None, None]:
        """Generate text using Victor backend"""
        if not self.loaded or not self.victor_module:
            raise RuntimeError("Victor backend not loaded")
        
        if not hasattr(self.victor_module, 'infer'):
            raise NotImplementedError("Victor backend does not implement 'infer' method")
        
        # Extract parameters
        prompt = request.get("prompt")
        messages = request.get("messages")
        
        params = {
            "temperature": request.get("temperature", self.manifest.get("defaults", {}).get("temperature", 0.7)),
            "top_p": request.get("top_p", self.manifest.get("defaults", {}).get("top_p", 0.9)),
            "max_tokens": request.get("max_tokens", self.manifest.get("defaults", {}).get("max_tokens", 256)),
            "stop": request.get("stop", [])
        }
        
        try:
            # Call Victor's infer method
            if messages:
                result = self.victor_module.infer(messages=messages, params=params)
            else:
                result = self.victor_module.infer(prompt=prompt, params=params)
            
            # Handle streaming response
            if isinstance(result, dict) and "stream" in result and result["stream"]:
                # Victor provides a generator
                for token in result["stream"]:
                    yield token
            elif isinstance(result, dict) and "text" in result:
                # Victor provides full text
                yield result["text"]
            else:
                # Assume result is the text itself
                yield str(result)
                
        except Exception as e:
            logger.error(f"Victor generation error: {e}")
            raise
    
    def trace(self, prompt: str, desired: str = None, methods: list = None) -> Dict[str, Any]:
        """Run tracing using Victor backend"""
        if not self.loaded or not self.victor_module:
            raise RuntimeError("Victor backend not loaded")
        
        if hasattr(self.victor_module, 'trace'):
            return self.victor_module.trace(prompt, desired, methods or ["grad_act"])
        
        return {"error": "Victor backend does not support tracing"}
    
    def causal_test(self, targets: list, prompt: str, method: str, baseline_prompt: str = None) -> Dict[str, Any]:
        """Run causal testing using Victor backend"""
        if not self.loaded or not self.victor_module:
            raise RuntimeError("Victor backend not loaded")
        
        if hasattr(self.victor_module, 'causal_test'):
            return self.victor_module.causal_test(targets, prompt, method, baseline_prompt)
        
        return {"error": "Victor backend does not support causal testing"}
    
    def train_target(self, strategy: str, targets: list, params: dict, dataset: dict) -> Dict[str, Any]:
        """Run targeted training using Victor backend"""
        if not self.loaded or not self.victor_module:
            raise RuntimeError("Victor backend not loaded")
        
        if hasattr(self.victor_module, 'train_target'):
            return self.victor_module.train_target(strategy, targets, params, dataset)
        
        return {"error": "Victor backend does not support targeted training"}
    
    def diagnostics(self, modes: list) -> Dict[str, Any]:
        """Run diagnostics using Victor backend"""
        if not self.loaded or not self.victor_module:
            raise RuntimeError("Victor backend not loaded")
        
        if hasattr(self.victor_module, 'diagnostics'):
            return self.victor_module.diagnostics(modes)
        
        return {"error": "Victor backend does not support diagnostics"}
