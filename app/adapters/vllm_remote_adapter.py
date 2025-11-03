"""
vLLM remote adapter for remote inference endpoints
"""
from typing import Dict, Any, Generator
from app.adapters import ModelAdapter
import logging

logger = logging.getLogger(__name__)


class VLLMRemoteAdapter(ModelAdapter):
    """Adapter for remote vLLM endpoints"""
    
    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.endpoint = None
        self.client = None
        
    def load(self) -> None:
        """Initialize connection to remote endpoint"""
        try:
            import httpx
            
            # Extract endpoint URL from manifest
            self.endpoint = self.manifest["files"].get("weights", "")  # URL stored in weights field
            
            if not self.endpoint.startswith("http"):
                raise ValueError(f"Invalid vLLM endpoint URL: {self.endpoint}")
            
            logger.info(f"Connecting to vLLM endpoint: {self.endpoint}")
            
            # Create HTTP client
            self.client = httpx.AsyncClient(timeout=300.0)
            self.loaded = True
            
            logger.info(f"Successfully connected to vLLM endpoint {self.manifest['id']}")
            
        except Exception as e:
            logger.error(f"Failed to connect to vLLM endpoint: {e}")
            raise
    
    def unload(self) -> None:
        """Close connection"""
        if self.client:
            import asyncio
            try:
                asyncio.get_event_loop().run_until_complete(self.client.aclose())
            except:
                pass
            self.client = None
        self.loaded = False
        logger.info(f"Disconnected from endpoint {self.manifest['id']}")
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """Tokenize text via remote endpoint"""
        if not self.loaded:
            raise RuntimeError("Endpoint not connected")
        
        # vLLM doesn't expose tokenization endpoint by default
        # Return approximate token count
        # Rough estimate: ~4 chars per token
        estimated_tokens = len(text) // 4
        
        return {
            "tokens": [],  # Not available from remote
            "ids": [],
            "count": estimated_tokens
        }
    
    def generate(self, request: Dict[str, Any]) -> Generator[str, None, None]:
        """Generate text via remote endpoint with streaming"""
        if not self.loaded or not self.client:
            raise RuntimeError("Endpoint not connected")
        
        import httpx
        import json
        import asyncio
        
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
        
        # Prepare request payload for vLLM
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            # Use synchronous httpx for streaming
            with httpx.Client(timeout=300.0) as sync_client:
                with sync_client.stream(
                    "POST",
                    f"{self.endpoint}/v1/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    token = data["choices"][0].get("text", "")
                                    if token:
                                        yield token
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Remote generation error: {e}")
            raise
    
    def _format_messages(self, messages: list) -> str:
        """Format messages for remote endpoint"""
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
