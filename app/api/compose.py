"""
Composer API - Merge and compose LoRA deltas
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.engines.compose import DeltaComposer

logger = logging.getLogger(__name__)

router = APIRouter()

# Global composer instance
delta_composer = DeltaComposer()


class MergeLoRARequest(BaseModel):
    """Request to merge LoRA deltas"""
    delta_ids: List[str]
    weights: Optional[List[float]] = None
    orthogonalize: bool = True


@router.post("/merge_lora")
async def merge_lora_deltas(request: MergeLoRARequest):
    """
    Merge multiple LoRA deltas into a single composed delta.
    
    Supports:
    - Layer-wise scaling
    - Orthogonalization to reduce interference
    - Conflict resolution
    """
    try:
        logger.info(f"Merging {len(request.delta_ids)} LoRA deltas")
        
        result = delta_composer.merge_deltas(
            delta_ids=request.delta_ids,
            weights=request.weights,
            orthogonalize=request.orthogonalize
        )
        
        return result
    except Exception as e:
        logger.error(f"Merge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deltas")
async def list_deltas():
    """
    List available delta checkpoints.
    """
    try:
        # In production, scan lab/deltas directory
        deltas = []
        
        return {
            "deltas": deltas,
            "count": len(deltas)
        }
    except Exception as e:
        logger.error(f"List error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
