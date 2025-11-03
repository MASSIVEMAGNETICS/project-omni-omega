"""
HuggingFace Transformers adapter
"""
from typing import Dict, Any, Generator
from app.adapters import ModelAdapter
import logging

logger = logging.getLogger(__name__)


class HFTransformersAdapter(ModelAdapter):
    """Adapter for HuggingFace Transformers models"""
    
    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.model = None
        self.tokenizer = None
        
    def load(self) -> None:
        """Load HuggingFace model"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            weights_path = self.manifest["files"]["weights"]
            tokenizer_path = self.manifest["files"].get("tokenizer", weights_path)
            
            logger.info(f"Loading HuggingFace model from {weights_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                tokenizer_path,
                trust_remote_code=False
            )
            
            # Load model (CPU-only by default)
            self.model = AutoModelForCausalLM.from_pretrained(
                weights_path,
                torch_dtype=torch.float32,  # CPU-safe
                device_map="cpu",
                low_cpu_mem_usage=True,
                trust_remote_code=False
            )
            
            self.model.eval()
            self.loaded = True
            logger.info(f"Successfully loaded model {self.manifest['id']}")
            
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            raise
    
    def unload(self) -> None:
        """Unload the model"""
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        self.loaded = False
        logger.info(f"Unloaded model {self.manifest['id']}")
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """Tokenize text"""
        if not self.loaded or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        encoded = self.tokenizer(text, return_tensors=None)
        tokens = self.tokenizer.convert_ids_to_tokens(encoded["input_ids"])
        
        return {
            "tokens": tokens,
            "ids": encoded["input_ids"],
            "count": len(encoded["input_ids"])
        }
    
    def generate(self, request: Dict[str, Any]) -> Generator[str, None, None]:
        """Generate text with streaming"""
        if not self.loaded or not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        import torch
        
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
        
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"]
            
            # Generate with streaming simulation
            with torch.no_grad():
                generated_tokens = []
                past_key_values = None
                
                for _ in range(max_tokens):
                    outputs = self.model(
                        input_ids=input_ids if past_key_values is None else input_ids[:, -1:],
                        past_key_values=past_key_values,
                        use_cache=True
                    )
                    
                    # Sample next token
                    logits = outputs.logits[:, -1, :]
                    
                    # Apply temperature
                    if temperature > 0:
                        logits = logits / temperature
                        
                        # Apply top-p sampling
                        if top_p < 1.0:
                            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                            cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                            sorted_indices_to_remove = cumulative_probs > top_p
                            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                            sorted_indices_to_remove[..., 0] = 0
                            indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                            logits[indices_to_remove] = float('-inf')
                    
                        probs = torch.softmax(logits, dim=-1)
                        next_token = torch.multinomial(probs, num_samples=1)
                    else:
                        next_token = torch.argmax(logits, dim=-1, keepdim=True)
                    
                    # Decode and yield token
                    token_text = self.tokenizer.decode(next_token[0], skip_special_tokens=True)
                    
                    # Check stop conditions
                    if any(stop_str in token_text for stop_str in stop):
                        break
                    
                    if next_token.item() == self.tokenizer.eos_token_id:
                        break
                    
                    yield token_text
                    
                    # Update for next iteration
                    input_ids = next_token
                    past_key_values = outputs.past_key_values
                    
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    def _format_messages(self, messages: list) -> str:
        """Format messages according to model's prompt template"""
        template = self.manifest.get("prompt_template", {})
        
        # Try to use tokenizer's chat template if available
        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            except:
                pass
        
        if template.get("chat"):
            formatted = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                formatted += template["chat"].format(role=role, content=content)
            return formatted
        else:
            return "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
