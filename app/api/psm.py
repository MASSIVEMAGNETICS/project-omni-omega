"""
PSM (Persistent State Memory) API - World model and memory management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from app.engines.psm import PSMStore

logger = logging.getLogger(__name__)

router = APIRouter()

# PSM stores keyed by model ID
psm_stores: Dict[str, PSMStore] = {}


class EventRequest(BaseModel):
    """Request to log an event"""
    model_id: str
    event: Dict[str, Any]


class ContextPackRequest(BaseModel):
    """Request for context pack"""
    model_id: str
    query: str
    k: int = 6


class SnapshotRequest(BaseModel):
    """Request to create PSM snapshot"""
    model_id: str
    snapshot_id: str
    description: Optional[str] = ""


def get_or_create_psm(model_id: str) -> PSMStore:
    """Get or create PSM store for a model"""
    if model_id not in psm_stores:
        store_dir = f"psm/{model_id}"
        psm_stores[model_id] = PSMStore(store_dir=store_dir)
    return psm_stores[model_id]


@router.post("/event")
async def log_event(request: EventRequest):
    """
    Log an event to PSM.
    
    Events are append-only and enable replay/debugging.
    """
    try:
        psm = get_or_create_psm(request.model_id)
        event_id = psm.append_event(request.event)
        
        return {
            "status": "success",
            "event_id": event_id
        }
    except Exception as e:
        logger.error(f"Event logging error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/context_pack")
async def get_context_pack(request: ContextPackRequest):
    """
    Get a context pack from PSM.
    
    Retrieves relevant entities and relations for a query.
    """
    try:
        psm = get_or_create_psm(request.model_id)
        context_pack = psm.get_context_pack(request.query, k=request.k)
        
        return context_pack
    except Exception as e:
        logger.error(f"Context pack error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snapshot")
async def create_snapshot(request: SnapshotRequest):
    """
    Create a snapshot of PSM state.
    
    Enables rollback and state management.
    """
    try:
        psm = get_or_create_psm(request.model_id)
        snapshot = psm.create_snapshot(request.snapshot_id, request.description)
        
        return snapshot
    except Exception as e:
        logger.error(f"Snapshot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{model_id}")
async def get_psm_stats(model_id: str):
    """
    Get PSM statistics for a model.
    """
    try:
        psm = get_or_create_psm(model_id)
        
        # Basic stats
        stats = {
            "model_id": model_id,
            "store_dir": str(psm.store_dir),
            "vector_dim": psm.vector_dim,
            # In production, add:
            # - Entity count
            # - Relation count
            # - Event count
            # - Storage size
        }
        
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
