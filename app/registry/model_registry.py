"""
Model Registry for discovering and managing models
"""
import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from app.schemas import ModelManifest, AdapterType
from app.adapters.llama_cpp_adapter import LlamaCppAdapter
from app.adapters.hf_transformers_adapter import HFTransformersAdapter
from app.adapters.vllm_remote_adapter import VLLMRemoteAdapter
from app.adapters.onnx_runtime_adapter import ONNXRuntimeAdapter
from app.adapters.victor_custom_adapter import VictorCustomAdapter
from app.adapters.aai_psm_adapter import AAIPSMAdapter
from app.adapters.induction_adapter import InductionAdapter

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Registry for discovering, validating, and managing models
    """
    
    ADAPTER_MAP = {
        AdapterType.LLAMA_CPP: LlamaCppAdapter,
        AdapterType.HF_TRANSFORMERS: HFTransformersAdapter,
        AdapterType.VLLM_REMOTE: VLLMRemoteAdapter,
        AdapterType.ONNX_RUNTIME: ONNXRuntimeAdapter,
        AdapterType.VICTOR_CUSTOM: VictorCustomAdapter,
        AdapterType.AAI_PSM: AAIPSMAdapter,
        AdapterType.INDUCTION: InductionAdapter,
    }
    
    def __init__(self, models_dir: str, victor_dir: str):
        """
        Initialize the model registry.
        
        Args:
            models_dir: Directory containing model manifests
            victor_dir: Directory for Victor custom backend
        """
        self.models_dir = Path(models_dir)
        self.victor_dir = Path(victor_dir)
        self.manifests: Dict[str, Dict[str, Any]] = {}
        self.adapters: Dict[str, Any] = {}
        
        # Create directories if they don't exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.victor_dir.mkdir(parents=True, exist_ok=True)
    
    def scan(self) -> List[str]:
        """
        Scan models directory for manifests.
        
        Returns:
            List of discovered model IDs
        """
        discovered = []
        
        # Scan models directory
        for root, dirs, files in os.walk(self.models_dir):
            for file in files:
                if file in ["manifest.json", "manifest.yaml", "manifest.yml"]:
                    manifest_path = os.path.join(root, file)
                    try:
                        manifest = self._load_manifest(manifest_path)
                        if manifest:
                            model_id = manifest.get("id")
                            if model_id:
                                # Make paths absolute relative to manifest location
                                manifest = self._resolve_paths(manifest, Path(root))
                                self.manifests[model_id] = manifest
                                discovered.append(model_id)
                                logger.info(f"Discovered model: {model_id}")
                    except Exception as e:
                        logger.error(f"Failed to load manifest {manifest_path}: {e}")
        
        # Scan victor directory
        if self.victor_dir.exists():
            victor_manifest_paths = [
                self.victor_dir / "manifest.json",
                self.victor_dir / "manifest.yaml",
                self.victor_dir / "manifest.yml"
            ]
            
            for manifest_path in victor_manifest_paths:
                if manifest_path.exists():
                    try:
                        manifest = self._load_manifest(str(manifest_path))
                        if manifest:
                            model_id = manifest.get("id", "victor_default")
                            manifest["adapter"] = "victor_custom"
                            manifest = self._resolve_paths(manifest, self.victor_dir)
                            self.manifests[model_id] = manifest
                            discovered.append(model_id)
                            logger.info(f"Discovered Victor model: {model_id}")
                    except Exception as e:
                        logger.error(f"Failed to load Victor manifest: {e}")
                    break
        
        logger.info(f"Discovered {len(discovered)} models")
        return discovered
    
    def register(self, manifest: Dict[str, Any]) -> str:
        """
        Register a model manifest.
        
        Args:
            manifest: Model manifest dictionary
            
        Returns:
            Model ID
        """
        # Validate manifest
        validated = ModelManifest(**manifest)
        model_id = validated.id
        
        # Store manifest
        self.manifests[model_id] = manifest
        logger.info(f"Registered model: {model_id}")
        
        return model_id
    
    def get_manifest(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get manifest for a model"""
        return self.manifests.get(model_id)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models"""
        models = []
        for model_id, manifest in self.manifests.items():
            models.append({
                "id": model_id,
                "name": manifest.get("name", model_id),
                "adapter": manifest.get("adapter"),
                "loaded": model_id in self.adapters and self.adapters[model_id].loaded,
                "context_length": manifest.get("context_length", 2048)
            })
        return models
    
    def load_model(self, model_id: str) -> None:
        """
        Load a model.
        
        Args:
            model_id: Model ID to load
        """
        if model_id not in self.manifests:
            raise ValueError(f"Model {model_id} not found in registry")
        
        # Unload if already loaded
        if model_id in self.adapters:
            self.unload_model(model_id)
        
        manifest = self.manifests[model_id]
        adapter_type = manifest.get("adapter")
        
        if adapter_type not in self.ADAPTER_MAP:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
        
        # Create and load adapter
        adapter_class = self.ADAPTER_MAP[AdapterType(adapter_type)]
        adapter = adapter_class(manifest)
        adapter.load()
        
        self.adapters[model_id] = adapter
        logger.info(f"Loaded model: {model_id}")
    
    def unload_model(self, model_id: str) -> None:
        """
        Unload a model.
        
        Args:
            model_id: Model ID to unload
        """
        if model_id in self.adapters:
            self.adapters[model_id].unload()
            del self.adapters[model_id]
            logger.info(f"Unloaded model: {model_id}")
    
    def get_adapter(self, model_id: str):
        """Get loaded adapter for a model"""
        if model_id not in self.adapters:
            raise ValueError(f"Model {model_id} not loaded")
        return self.adapters[model_id]
    
    def _load_manifest(self, path: str) -> Optional[Dict[str, Any]]:
        """Load manifest from file"""
        try:
            with open(path, 'r') as f:
                if path.endswith('.json'):
                    return json.load(f)
                else:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load manifest {path}: {e}")
            return None
    
    def _resolve_paths(self, manifest: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
        """Resolve relative paths in manifest to absolute paths"""
        if "files" in manifest:
            files = manifest["files"]
            
            # Resolve weights path
            if "weights" in files and files["weights"]:
                weights = files["weights"]
                # Skip URL resolution for remote endpoints
                if not weights.startswith("http"):
                    weights_path = Path(weights)
                    if not weights_path.is_absolute():
                        files["weights"] = str(base_dir / weights_path)
            
            # Resolve tokenizer path
            if "tokenizer" in files and files["tokenizer"]:
                tokenizer_path = Path(files["tokenizer"])
                if not tokenizer_path.is_absolute():
                    files["tokenizer"] = str(base_dir / tokenizer_path)
            
            # Resolve config path
            if "config" in files and files["config"]:
                config_path = Path(files["config"])
                if not config_path.is_absolute():
                    files["config"] = str(base_dir / config_path)
        
        return manifest
