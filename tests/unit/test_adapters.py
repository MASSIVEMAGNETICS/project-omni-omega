"""
Unit tests for model adapters
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.adapters.llama_cpp_adapter import LlamaCppAdapter
from app.adapters.hf_transformers_adapter import HFTransformersAdapter
from app.adapters.vllm_remote_adapter import VLLMRemoteAdapter
from app.adapters.onnx_runtime_adapter import ONNXRuntimeAdapter
from app.adapters.victor_custom_adapter import VictorCustomAdapter


class TestAdapterInterface:
    """Test that all adapters implement the required interface"""
    
    def test_llama_cpp_adapter_interface(self):
        """Test LlamaCppAdapter has required methods"""
        manifest = {
            "id": "test",
            "adapter": "llama_cpp",
            "files": {"weights": "test.gguf"}
        }
        adapter = LlamaCppAdapter(manifest)
        
        assert hasattr(adapter, 'load')
        assert hasattr(adapter, 'unload')
        assert hasattr(adapter, 'tokenize')
        assert hasattr(adapter, 'generate')
        assert hasattr(adapter, 'get_model_info')
    
    def test_hf_transformers_adapter_interface(self):
        """Test HFTransformersAdapter has required methods"""
        manifest = {
            "id": "test",
            "adapter": "hf_transformers",
            "files": {"weights": "test"}
        }
        adapter = HFTransformersAdapter(manifest)
        
        assert hasattr(adapter, 'load')
        assert hasattr(adapter, 'unload')
        assert hasattr(adapter, 'tokenize')
        assert hasattr(adapter, 'generate')
    
    def test_vllm_remote_adapter_interface(self):
        """Test VLLMRemoteAdapter has required methods"""
        manifest = {
            "id": "test",
            "adapter": "vllm_remote",
            "files": {"weights": "http://localhost:8001"}
        }
        adapter = VLLMRemoteAdapter(manifest)
        
        assert hasattr(adapter, 'load')
        assert hasattr(adapter, 'unload')
        assert hasattr(adapter, 'tokenize')
        assert hasattr(adapter, 'generate')
    
    def test_onnx_runtime_adapter_interface(self):
        """Test ONNXRuntimeAdapter has required methods"""
        manifest = {
            "id": "test",
            "adapter": "onnx_runtime",
            "files": {"weights": "test.onnx"}
        }
        adapter = ONNXRuntimeAdapter(manifest)
        
        assert hasattr(adapter, 'load')
        assert hasattr(adapter, 'unload')
        assert hasattr(adapter, 'tokenize')
        assert hasattr(adapter, 'generate')
    
    def test_victor_custom_adapter_interface(self):
        """Test VictorCustomAdapter has required methods"""
        manifest = {
            "id": "test",
            "adapter": "victor_custom",
            "files": {"weights": "."}
        }
        adapter = VictorCustomAdapter(manifest)
        
        assert hasattr(adapter, 'load')
        assert hasattr(adapter, 'unload')
        assert hasattr(adapter, 'tokenize')
        assert hasattr(adapter, 'generate')
        assert hasattr(adapter, 'trace')
        assert hasattr(adapter, 'causal_test')
        assert hasattr(adapter, 'train_target')
        assert hasattr(adapter, 'diagnostics')


class TestAdapterInitialization:
    """Test adapter initialization"""
    
    def test_adapter_manifest_storage(self):
        """Test that adapters store manifest"""
        manifest = {
            "id": "test-model",
            "name": "Test Model",
            "adapter": "llama_cpp",
            "files": {"weights": "test.gguf"}
        }
        adapter = LlamaCppAdapter(manifest)
        
        assert adapter.manifest == manifest
        assert adapter.manifest["id"] == "test-model"
        assert adapter.loaded == False
    
    def test_get_model_info(self):
        """Test get_model_info method"""
        manifest = {
            "id": "test-model",
            "name": "Test Model",
            "adapter": "llama_cpp",
            "files": {"weights": "test.gguf"},
            "context_length": 2048
        }
        adapter = LlamaCppAdapter(manifest)
        
        info = adapter.get_model_info()
        assert info["id"] == "test-model"
        assert info["name"] == "Test Model"
        assert info["adapter"] == "llama_cpp"
        assert info["loaded"] == False
        assert info["context_length"] == 2048


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
