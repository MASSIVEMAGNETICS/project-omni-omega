"""
Main FastAPI application for OmniLoader
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.registry import ModelRegistry
from app.engines import DiagnosticsEngine, TraceTargetEngine, LiveTrainEngine
from app.api import routes, lab_routes
from app.api import brainbuilder, otl, psm, compose

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="OmniLoader - Production-grade local-first AI model manager"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
logger.info("Initializing OmniLoader components...")

# Model registry
registry = ModelRegistry(
    models_dir=settings.models_dir,
    victor_dir=settings.victor_dir
)

# Lab engines
diagnostics_engine = DiagnosticsEngine(lab_dir=settings.lab_dir)
trace_target_engine = TraceTargetEngine(lab_dir=settings.lab_dir)
live_train_engine = LiveTrainEngine(lab_dir=settings.lab_dir)

# Inject dependencies into route modules
routes.set_registry(registry)
lab_routes.set_engines(registry, diagnostics_engine, trace_target_engine, live_train_engine)

# Include routers
app.include_router(routes.router, prefix="/api", tags=["core"])
app.include_router(lab_routes.router, prefix="/api", tags=["lab"])
app.include_router(brainbuilder.router, prefix="/api/lab/brain", tags=["brain"])
app.include_router(otl.router, prefix="/api/otl", tags=["otl"])
app.include_router(psm.router, prefix="/api/psm", tags=["psm"])
app.include_router(compose.router, prefix="/api/compose", tags=["compose"])


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("OmniLoader API starting up...")
    
    # Scan for models
    logger.info("Scanning for models...")
    discovered = registry.scan()
    logger.info(f"Discovered {len(discovered)} models: {discovered}")
    
    logger.info("OmniLoader API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("OmniLoader API shutting down...")
    
    # Unload all models
    for model_id in list(registry.adapters.keys()):
        try:
            registry.unload_model(model_id)
        except:
            pass
    
    logger.info("OmniLoader API stopped.")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "OmniLoader API",
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False
    )
