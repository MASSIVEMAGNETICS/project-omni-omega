"""
Tests for Transfer Learning components
"""
import pytest
import numpy as np

from app.engines.transfer import Distiller, FeatureBridge


class TestDistiller:
    """Test knowledge distillation"""
    
    def test_init(self):
        """Test distiller initialization"""
        distiller = Distiller(temperature=2.0, alpha=0.5)
        
        assert distiller.temperature == 2.0
        assert distiller.alpha == 0.5
    
    def test_distill(self):
        """Test distillation workflow"""
        distiller = Distiller()
        
        examples = [
            {"prompt": "What is 2+2?", "response": "4"},
            {"prompt": "What is AI?", "response": "Artificial Intelligence"}
        ]
        
        result = distiller.distill(
            teacher_model_id="large-model",
            student_model_id="small-model",
            examples=examples,
            steps=50
        )
        
        assert result["status"] == "success"
        assert result["teacher_id"] == "large-model"
        assert result["student_id"] == "small-model"
        assert "metrics" in result


class TestFeatureBridge:
    """Test feature space mapping"""
    
    def test_init(self):
        """Test feature bridge initialization"""
        bridge = FeatureBridge(source_dim=512, target_dim=768)
        
        assert bridge.source_dim == 512
        assert bridge.target_dim == 768
    
    def test_learn_mapping(self):
        """Test learning feature mapping"""
        bridge = FeatureBridge(source_dim=4, target_dim=6)
        
        # Generate sample features
        n_samples = 100
        source_features = np.random.randn(n_samples, 4).astype(np.float32)
        target_features = np.random.randn(n_samples, 6).astype(np.float32)
        
        result = bridge.learn_mapping(source_features, target_features)
        
        assert result["status"] == "success"
        assert "reconstruction_mse" in result
        assert bridge.projection is not None
        assert bridge.projection.shape == (4, 6)
    
    def test_map_features(self):
        """Test mapping features to target space"""
        bridge = FeatureBridge(source_dim=4, target_dim=6)
        
        # Learn mapping first
        n_samples = 50
        source_features = np.random.randn(n_samples, 4).astype(np.float32)
        target_features = np.random.randn(n_samples, 6).astype(np.float32)
        bridge.learn_mapping(source_features, target_features)
        
        # Map new features
        new_source = np.random.randn(10, 4).astype(np.float32)
        mapped = bridge.map_features(new_source)
        
        assert mapped.shape == (10, 6)
    
    def test_map_direction(self):
        """Test mapping direction vectors"""
        bridge = FeatureBridge(source_dim=4, target_dim=6)
        
        # Learn mapping
        n_samples = 50
        source_features = np.random.randn(n_samples, 4).astype(np.float32)
        target_features = np.random.randn(n_samples, 6).astype(np.float32)
        bridge.learn_mapping(source_features, target_features)
        
        # Map a direction
        source_direction = np.array([1, 0, 0, 0], dtype=np.float32)
        target_direction = bridge.map_direction(source_direction)
        
        assert target_direction.shape == (6,)
        # Check normalized
        assert abs(np.linalg.norm(target_direction) - 1.0) < 1e-5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
