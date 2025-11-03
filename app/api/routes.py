"""
Core API routes for model management and generation
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import uuid
import logging

from app.schemas import (
    GenerateRequest, SessionRequest, SessionResponse,
    ModelInfo, ModelManifest
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Global registry and session storage (injected by main app)
_registry = None
_sessions = {}


def set_registry(registry):
    """Set the global model registry"""
    global _registry
    _registry = registry


@router.post("/models/register")
async def register_model(manifest: ModelManifest) -> Dict[str, str]:
    """Register a new model manifest"""
    try:
        model_id = _registry.register(manifest.dict())
        return {"model_id": model_id, "status": "registered"}
    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """List all registered models"""
    try:
        models = _registry.list_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/load")
async def load_model(model_id: str) -> Dict[str, str]:
    """Load a model"""
    try:
        _registry.load_model(model_id)
        return {"model_id": model_id, "status": "loaded"}
    except Exception as e:
        logger.error(f"Failed to load model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/unload")
async def unload_model(model_id: str) -> Dict[str, str]:
    """Unload a model"""
    try:
        _registry.unload_model(model_id)
        return {"model_id": model_id, "status": "unloaded"}
    except Exception as e:
        logger.error(f"Failed to unload model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session")
async def create_session(request: SessionRequest) -> SessionResponse:
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            "model_id": request.model_id,
            "system_prompt": request.system_prompt,
            "history": []
        }
        return SessionResponse(session_id=session_id, model_id=request.model_id)
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate(request: GenerateRequest):
    """Generate text with streaming support"""
    try:
        adapter = _registry.get_adapter(request.model_id)
        
        # Build generation request
        gen_request = {
            "prompt": request.prompt,
            "messages": request.messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens,
            "stop": request.stop
        }
        
        if request.stream:
            # Server-Sent Events streaming
            async def event_generator():
                try:
                    for token in adapter.generate(gen_request):
                        yield f"data: {token}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    yield f"data: [ERROR: {str(e)}]\n\n"
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream"
            )
        else:
            # Non-streaming response
            tokens = []
            for token in adapter.generate(gen_request):
                tokens.append(token)
            
            return {
                "model_id": request.model_id,
                "text": "".join(tokens)
            }
            
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/tokenize")
async def tokenize(model_id: str, text: str) -> Dict[str, Any]:
    """Tokenize text"""
    try:
        adapter = _registry.get_adapter(model_id)
        result = adapter.tokenize(text)
        return result
    except Exception as e:
        logger.error(f"Tokenization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
