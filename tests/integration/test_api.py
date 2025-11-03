"""
Integration tests for API endpoints
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.main import app

client = TestClient(app)


class TestCoreEndpoints:
    """Test core API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_list_models_endpoint(self):
        """Test list models endpoint"""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)
    
    def test_register_model_endpoint(self):
        """Test model registration endpoint"""
        manifest = {
            "id": "test-api-model",
            "name": "Test API Model",
            "adapter": "llama_cpp",
            "files": {
                "weights": "test.gguf"
            },
            "context_length": 2048,
            "defaults": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 256,
                "threads": 2
            }
        }
        
        response = client.post("/api/models/register", json=manifest)
        assert response.status_code == 200
        data = response.json()
        assert "model_id" in data
        assert data["model_id"] == "test-api-model"


class TestLabEndpoints:
    """Test Lab API endpoints"""
    
    def test_queue_endpoint(self):
        """Test training queue endpoint"""
        example = {
            "prompt": "Test prompt",
            "chosen": "Good response"
        }
        
        response = client.post("/api/lab/queue", json=example)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "added"
        
        # Get queue
        response = client.get("/api/lab/queue")
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
        assert "count" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
