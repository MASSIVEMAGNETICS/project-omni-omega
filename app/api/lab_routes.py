"""
Lab API routes for diagnostics, tracing, and training
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

from app.schemas import (
    DiagnosticsRequest, TraceRequest, CausalTestRequest,
    TrainTargetRequest, LiveTrainRequest, SnapshotRequest,
    AuraRequest, SkillPackRequest, QueueExample
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lab")

# Global engines and registry (injected by main app)
_registry = None
_diagnostics_engine = None
_trace_target_engine = None
_live_train_engine = None


def set_engines(registry, diagnostics, trace_target, live_train):
    """Set the global engines"""
    global _registry, _diagnostics_engine, _trace_target_engine, _live_train_engine
    _registry = registry
    _diagnostics_engine = diagnostics
    _trace_target_engine = trace_target
    _live_train_engine = live_train


# Diagnostics routes
@router.post("/diagnostics/run")
async def run_diagnostics(request: DiagnosticsRequest) -> Dict[str, Any]:
    """Run diagnostics on a model"""
    try:
        adapter = _registry.get_adapter(request.model_id)
        report = _diagnostics_engine.run_diagnostics(
            adapter,
            request.model_id,
            request.modes,
            request.quick_mode
        )
        return report
    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diagnostics/report")
async def get_diagnostic_report(
    model_id: str,
    report_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get a diagnostic report"""
    try:
        report = _diagnostics_engine.get_report(model_id, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Trace & Target routes
@router.post("/trace")
async def trace(request: TraceRequest) -> Dict[str, Any]:
    """Run causal tracing"""
    try:
        adapter = _registry.get_adapter(request.model_id)
        result = _trace_target_engine.trace(
            adapter,
            request.model_id,
            request.prompt,
            request.desired,
            request.methods,
            request.resolution
        )
        return result
    except Exception as e:
        logger.error(f"Tracing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/causal_test")
async def causal_test(request: CausalTestRequest) -> Dict[str, Any]:
    """Run causal intervention test"""
    try:
        adapter = _registry.get_adapter(request.model_id)
        result = _trace_target_engine.causal_test(
            adapter,
            request.model_id,
            request.prompt,
            [t.dict() for t in request.targets],
            request.method,
            request.baseline_prompt
        )
        return result
    except Exception as e:
        logger.error(f"Causal test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train/target")
async def train_target(request: TrainTargetRequest) -> Dict[str, Any]:
    """Run targeted training"""
    try:
        adapter = _registry.get_adapter(request.model_id)
        
        # Check if adapter supports targeted training (Victor backend)
        if hasattr(adapter, 'train_target'):
            result = adapter.train_target(
                request.strategy,
                [t.dict() for t in request.targets],
                request.params,
                request.dataset
            )
        else:
            result = {
                "status": "not_supported",
                "message": "Adapter does not support targeted training"
            }
        
        return result
    except Exception as e:
        logger.error(f"Targeted training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Live Training routes
@router.post("/queue")
async def add_to_queue(example: QueueExample) -> Dict[str, str]:
    """Add example to training queue"""
    try:
        _live_train_engine.add_to_queue(example.dict())
        return {"status": "added"}
    except Exception as e:
        logger.error(f"Failed to add to queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue")
async def get_queue(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get training queue"""
    try:
        examples = _live_train_engine.get_queue(limit)
        return {"examples": examples, "count": len(examples)}
    except Exception as e:
        logger.error(f"Failed to get queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train/live")
async def live_train(request: LiveTrainRequest) -> Dict[str, Any]:
    """Run live training"""
    try:
        adapter = _registry.get_adapter(request.model_id)
        result = _live_train_engine.live_train(
            adapter,
            request.model_id,
            request.mode,
            request.budget,
            request.dataset
        )
        return result
    except Exception as e:
        logger.error(f"Live training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Snapshot routes
@router.post("/snapshot")
async def create_snapshot(request: SnapshotRequest) -> Dict[str, str]:
    """Create a model snapshot"""
    try:
        snapshot_id = _live_train_engine.create_snapshot(
            request.model_id,
            request.description
        )
        return {"snapshot_id": snapshot_id, "status": "created"}
    except Exception as e:
        logger.error(f"Failed to create snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback")
async def rollback(model_id: str, snapshot_id: str) -> Dict[str, Any]:
    """Rollback model to snapshot"""
    try:
        result = _live_train_engine.rollback(model_id, snapshot_id)
        return result
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Aura routes
@router.post("/auras/create")
async def create_aura(request: AuraRequest) -> Dict[str, str]:
    """Create or update an Aura"""
    try:
        aura_id = _live_train_engine.create_aura(request.dict())
        return {"aura_id": aura_id, "status": "created"}
    except Exception as e:
        logger.error(f"Failed to create aura: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SkillPack routes
@router.post("/skillpack/export")
async def export_skillpack(request: SkillPackRequest) -> Dict[str, str]:
    """Export a SkillPack"""
    try:
        skillpack_id = _live_train_engine.export_skillpack(request.dict())
        return {"skillpack_id": skillpack_id, "status": "exported"}
    except Exception as e:
        logger.error(f"Failed to export skillpack: {e}")
        raise HTTPException(status_code=500, detail=str(e))
