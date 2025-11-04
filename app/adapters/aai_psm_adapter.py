"""
AAI+PSM Adapter - Augmented AI with Persistent State Memory

This adapter wraps an inner model with:
- Tool usage (filesystem, web search, etc.)
- Reflection/meta-cognition
- Persistent memory via PSM
- Plan-Retrieve-Answer workflow
"""
import logging
from typing import Dict, Any, Generator, Optional, List
import json

from app.adapters import ModelAdapter
from app.engines.psm import PSMStore

logger = logging.getLogger(__name__)


class AAIPSMAdapter(ModelAdapter):
    """
    Augmented AI + PSM adapter.
    
    Wraps an inner model with AAI capabilities and PSM integration.
    Follows: Plan → Retrieve (from PSM) → Answer workflow.
    """
    
    def __init__(self, manifest: Dict[str, Any]):
        """
        Initialize AAI+PSM adapter.
        
        Args:
            manifest: Model manifest with AAI and PSM configuration
        """
        super().__init__(manifest)
        
        self.aai_config = manifest.get("aai", {})
        self.inner_manifest = self.aai_config.get("inner_manifest", {})
        self.tools = self.aai_config.get("tools", [])
        self.reflection_config = self.aai_config.get("reflection", {})
        self.memory_config = self.aai_config.get("memory", {})
        
        self.inner_adapter = None
        self.psm_store = None
        
        logger.info(f"AAIPSMAdapter initialized for {manifest.get('id')}")
        logger.info(f"  Tools: {self.tools}")
        logger.info(f"  Reflection: {self.reflection_config.get('enabled', False)}")
        logger.info(f"  Memory: PSM with k={self.memory_config.get('k', 6)}")
    
    def load(self) -> None:
        """Load the inner model and initialize PSM"""
        logger.info("Loading AAI+PSM adapter...")
        
        # Load inner model adapter
        # In production, this would dynamically create the appropriate adapter
        # based on self.inner_manifest
        logger.info(f"Loading inner model: {self.inner_manifest.get('id')}")
        # Placeholder: self.inner_adapter = create_adapter(self.inner_manifest)
        
        # Initialize PSM store
        psm_dir = f"psm/{self.manifest['id']}"
        vector_dim = self.memory_config.get("vector_dim", 384)
        self.psm_store = PSMStore(store_dir=psm_dir, vector_dim=vector_dim)
        
        self.loaded = True
        logger.info("AAI+PSM adapter loaded successfully")
    
    def unload(self) -> None:
        """Unload the inner model"""
        if self.inner_adapter:
            # In production: self.inner_adapter.unload()
            pass
        
        self.loaded = False
        logger.info("AAI+PSM adapter unloaded")
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """Tokenize using inner model"""
        if not self.loaded:
            raise RuntimeError("Adapter not loaded")
        
        # In production, delegate to inner adapter
        # return self.inner_adapter.tokenize(text)
        
        # Placeholder
        tokens = text.split()
        return {
            "tokens": tokens,
            "ids": list(range(len(tokens))),
            "count": len(tokens)
        }
    
    def generate(self, request: Dict[str, Any]) -> Generator[str, None, None]:
        """
        Generate with AAI+PSM workflow: Plan → Retrieve → Answer
        
        Args:
            request: Generation request
            
        Yields:
            Generated tokens
        """
        if not self.loaded:
            raise RuntimeError("Adapter not loaded")
        
        prompt = request.get("prompt", "")
        
        # Log inference event to PSM
        event = {
            "type": "inference",
            "data": {
                "prompt": prompt,
                "temperature": request.get("temperature"),
                "max_tokens": request.get("max_tokens")
            }
        }
        event_id = self.psm_store.append_event(event)
        
        # Phase 1: Plan (if tools are available)
        plan = None
        if self.tools:
            plan = self._generate_plan(prompt)
            logger.info(f"Generated plan: {plan}")
        
        # Phase 2: Retrieve from PSM
        context_pack = self._retrieve_context(prompt)
        logger.info(f"Retrieved context: {len(context_pack['entities'])} entities")
        
        # Phase 3: Reflection (if enabled)
        if self.reflection_config.get("enabled", False):
            reflection = self._reflect(prompt, context_pack)
            logger.info(f"Reflection: {reflection}")
        
        # Phase 4: Generate answer
        # In production, this would augment the prompt with:
        # - Retrieved context
        # - Plan
        # - Tool outputs
        # - Reflection
        
        # For now, use simple generation with inner model
        # In production: yield from self.inner_adapter.generate(augmented_request)
        
        # Placeholder: simple echo response
        response = f"[AAI+PSM Response to: {prompt[:50]}...]"
        for token in response.split():
            yield token + " "
        
        # Log completion event
        completion_event = {
            "type": "completion",
            "data": {
                "event_id": event_id,
                "response": response
            }
        }
        self.psm_store.append_event(completion_event)
    
    def _generate_plan(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate an action plan for the prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            Plan dictionary or None
        """
        # Placeholder: In production, this would:
        # 1. Analyze the prompt
        # 2. Determine which tools are needed
        # 3. Generate a step-by-step plan
        
        if "file" in prompt.lower() and "filesystem" in self.tools:
            return {"action": "read_file", "tool": "filesystem"}
        
        return None
    
    def _retrieve_context(self, query: str) -> Dict[str, Any]:
        """
        Retrieve relevant context from PSM.
        
        Args:
            query: Query string
            
        Returns:
            Context pack with relevant entities
        """
        k = self.memory_config.get("k", 6)
        return self.psm_store.get_context_pack(query, k=k)
    
    def _reflect(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Generate reflection on the prompt and context.
        
        Args:
            prompt: User prompt
            context: Retrieved context
            
        Returns:
            Reflection text
        """
        budget = self.reflection_config.get("budget_tokens", 128)
        
        # Placeholder: In production, this would use the model to:
        # 1. Analyze the prompt
        # 2. Consider retrieved context
        # 3. Identify potential issues or improvements
        # 4. Generate meta-cognitive reflection
        
        return f"[Reflection within {budget} token budget]"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        info = super().get_model_info()
        info.update({
            "adapter_type": "aai_psm",
            "inner_model": self.inner_manifest.get("id"),
            "tools": self.tools,
            "reflection_enabled": self.reflection_config.get("enabled", False),
            "psm_vector_dim": self.memory_config.get("vector_dim", 384)
        })
        return info
