"""
Unit tests for model registry
"""
import pytest
import sys
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.registry.model_registry import ModelRegistry


class TestModelRegistry:
    """Test ModelRegistry functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.models_dir = Path(self.temp_dir) / "models"
        self.victor_dir = Path(self.temp_dir) / "victor"
        self.models_dir.mkdir(parents=True)
        self.victor_dir.mkdir(parents=True)
        
        self.registry = ModelRegistry(
            models_dir=str(self.models_dir),
            victor_dir=str(self.victor_dir)
        )
    
    def test_registry_initialization(self):
        """Test registry initialization"""
        assert self.registry.models_dir == self.models_dir
        assert self.registry.victor_dir == self.victor_dir
        assert isinstance(self.registry.manifests, dict)
        assert isinstance(self.registry.adapters, dict)
    
    def test_register_model(self):
        """Test model registration"""
        manifest = {
            "id": "test-model",
            "name": "Test Model",
            "adapter": "llama_cpp",
            "files": {"weights": "test.gguf"},
            "context_length": 2048,
            "defaults": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 256,
                "threads": 2
            }
        }
        
        model_id = self.registry.register(manifest)
        assert model_id == "test-model"
        assert "test-model" in self.registry.manifests
        assert self.registry.manifests["test-model"]["name"] == "Test Model"
    
    def test_get_manifest(self):
        """Test getting model manifest"""
        manifest = {
            "id": "test-model",
            "name": "Test Model",
            "adapter": "llama_cpp",
            "files": {"weights": "test.gguf"},
            "context_length": 2048,
            "defaults": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 256,
                "threads": 2
            }
        }
        
        self.registry.register(manifest)
        retrieved = self.registry.get_manifest("test-model")
        
        assert retrieved is not None
        assert retrieved["id"] == "test-model"
        assert retrieved["adapter"] == "llama_cpp"
    
    def test_list_models(self):
        """Test listing models"""
        manifest1 = {
            "id": "model-1",
            "name": "Model 1",
            "adapter": "llama_cpp",
            "files": {"weights": "test1.gguf"},
            "context_length": 2048,
            "defaults": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 256,
                "threads": 2
            }
        }
        
        manifest2 = {
            "id": "model-2",
            "name": "Model 2",
            "adapter": "hf_transformers",
            "files": {"weights": "test2"},
            "context_length": 4096,
            "defaults": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 256,
                "threads": 2
            }
        }
        
        self.registry.register(manifest1)
        self.registry.register(manifest2)
        
        models = self.registry.list_models()
        assert len(models) == 2
        assert any(m["id"] == "model-1" for m in models)
        assert any(m["id"] == "model-2" for m in models)
    
    def test_scan_models(self):
        """Test scanning for model manifests"""
        # Create a test model manifest file
        model_dir = self.models_dir / "test-model"
        model_dir.mkdir()
        
        manifest = {
            "id": "scanned-model",
            "name": "Scanned Model",
            "adapter": "llama_cpp",
            "files": {"weights": "model.gguf"},
            "context_length": 2048,
            "defaults": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 256,
                "threads": 2
            }
        }
        
        with open(model_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f)
        
        # Scan for models
        discovered = self.registry.scan()
        
        assert len(discovered) == 1
        assert "scanned-model" in discovered
        assert "scanned-model" in self.registry.manifests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
