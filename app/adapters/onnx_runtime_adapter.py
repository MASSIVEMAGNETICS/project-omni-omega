"""
ONNX Runtime adapter
"""
from typing import Dict, Any, Generator
from app.adapters import ModelAdapter
import logging

logger = logging.getLogger(__name__)


class ONNXRuntimeAdapter(ModelAdapter):
    """Adapter for ONNX Runtime models"""
    
    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.session = None
        self.tokenizer = None
        
    def load(self) -> None:
        """Load ONNX model"""
        try:
            import onnxruntime as ort
            import numpy as np
            
            weights_path = self.manifest["files"]["weights"]
            tokenizer_path = self.manifest["files"].get("tokenizer")
            
            logger.info(f"Loading ONNX model from {weights_path}")
            
            # Create ONNX Runtime session (CPU-only)
            sess_options = ort.SessionOptions()
            sess_options.inter_op_num_threads = 2
            sess_options.intra_op_num_threads = 2
            
            self.session = ort.InferenceSession(
                weights_path,
                sess_options=sess_options,
                providers=['CPUExecutionProvider']
            )
            
            # Load tokenizer if available
            if tokenizer_path:
                try:
                    from transformers import AutoTokenizer
                    self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
                except Exception as e:
                    logger.warning(f"Failed to load tokenizer: {e}")
                    self.tokenizer = None
            
            self.loaded = True
            logger.info(f"Successfully loaded ONNX model {self.manifest['id']}")
            
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            raise
    
    def unload(self) -> None:
        """Unload the model"""
        if self.session:
            del self.session
            self.session = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        self.loaded = False
        logger.info(f"Unloaded model {self.manifest['id']}")
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """Tokenize text"""
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        
        if self.tokenizer:
            encoded = self.tokenizer(text, return_tensors=None)
            tokens = self.tokenizer.convert_ids_to_tokens(encoded["input_ids"])
            
            return {
                "tokens": tokens,
                "ids": encoded["input_ids"],
                "count": len(encoded["input_ids"])
            }
        else:
            # Simple whitespace tokenization fallback
            tokens = text.split()
            return {
                "tokens": tokens,
                "ids": list(range(len(tokens))),
                "count": len(tokens)
            }
    
    def generate(self, request: Dict[str, Any]) -> Generator[str, None, None]:
        """Generate text with streaming simulation"""
        if not self.loaded or not self.session:
            raise RuntimeError("Model not loaded")
        
        import numpy as np
        
        # Extract parameters
        prompt = request.get("prompt", "")
        messages = request.get("messages")
        
        if messages:
            prompt = self._format_messages(messages)
        
        max_tokens = request.get("max_tokens", self.manifest.get("defaults", {}).get("max_tokens", 256))
        temperature = request.get("temperature", self.manifest.get("defaults", {}).get("temperature", 0.7))
        
        try:
            if not self.tokenizer:
                # Simple fallback for models without tokenizer
                yield f"[ONNX model response to: {prompt[:50]}...]"
                return
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="np")
            input_ids = inputs["input_ids"]
            attention_mask = inputs.get("attention_mask")
            
            # Get input names
            input_names = [inp.name for inp in self.session.get_inputs()]
            
            # Prepare feeds
            feeds = {}
            if "input_ids" in input_names:
                feeds["input_ids"] = input_ids.astype(np.int64)
            if "attention_mask" in input_names and attention_mask is not None:
                feeds["attention_mask"] = attention_mask.astype(np.int64)
            
            # Run inference (single pass - streaming simulation)
            outputs = self.session.run(None, feeds)
            
            # Get logits (assuming first output is logits)
            logits = outputs[0]
            
            # Sample tokens
            generated_tokens = []
            for i in range(min(max_tokens, 50)):  # Limit for ONNX
                if temperature > 0:
                    # Apply temperature and sample
                    probs = np.exp(logits[0, -1, :] / temperature)
                    probs = probs / np.sum(probs)
                    next_token = np.random.choice(len(probs), p=probs)
                else:
                    next_token = np.argmax(logits[0, -1, :])
                
                # Decode token
                token_text = self.tokenizer.decode([next_token], skip_special_tokens=True)
                
                if next_token == self.tokenizer.eos_token_id:
                    break
                
                yield token_text
                generated_tokens.append(next_token)
                
        except Exception as e:
            logger.error(f"ONNX generation error: {e}")
            # Fallback response
            yield f"[Error in ONNX generation: {str(e)}]"
    
    def _format_messages(self, messages: list) -> str:
        """Format messages"""
        template = self.manifest.get("prompt_template", {})
        
        if template.get("chat"):
            formatted = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                formatted += template["chat"].format(role=role, content=content)
            return formatted
        else:
            return "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
