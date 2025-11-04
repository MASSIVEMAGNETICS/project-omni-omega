"""
OTL (Open Transfer Learning) API - Share and import training artifacts
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class PushSampleRequest(BaseModel):
    """Request to push training samples"""
    model_id: str
    samples: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class PullArtifactRequest(BaseModel):
    """Request to pull a training artifact"""
    artifact_id: str
    artifact_type: str  # 'delta', 'skillpack', 'aura'


@router.get("/manifest")
async def get_otl_manifest():
    """
    Get OTL manifest with available artifacts.
    
    Returns metadata for artifacts that can be pulled.
    """
    # In production, this would query a local or remote artifact registry
    manifest = {
        "version": "1.0",
        "artifacts": [
            {
                "id": "example_delta_1",
                "type": "delta",
                "model_family": "llama",
                "description": "Math reasoning improvement",
                "size_mb": 2.5,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
    
    return manifest


@router.post("/samples/push")
async def push_samples(request: PushSampleRequest):
    """
    Push training samples to OTL registry.
    
    Enables sharing curated training data.
    """
    try:
        logger.info(f"Pushing {len(request.samples)} samples for {request.model_id}")
        
        # In production:
        # 1. Validate samples
        # 2. Sign with provenance
        # 3. Store in local registry
        # 4. Optionally sync to remote
        
        result = {
            "status": "success",
            "samples_pushed": len(request.samples),
            "artifact_id": f"samples_{request.model_id}"
        }
        
        return result
    except Exception as e:
        logger.error(f"Push error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/artifact/pull")
async def pull_artifact(request: PullArtifactRequest):
    """
    Pull a training artifact from OTL registry.
    
    Downloads deltas, skillpacks, or auras.
    """
    try:
        logger.info(f"Pulling artifact: {request.artifact_id} ({request.artifact_type})")
        
        # In production:
        # 1. Verify artifact signature
        # 2. Check compatibility
        # 3. Download to local registry
        # 4. Make available for use
        
        result = {
            "status": "success",
            "artifact_id": request.artifact_id,
            "artifact_type": request.artifact_type,
            "local_path": f"lab/{request.artifact_type}s/{request.artifact_id}"
        }
        
        return result
    except Exception as e:
        logger.error(f"Pull error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
