"""
Tests for DeltaComposer
"""
import pytest

from app.engines.compose import DeltaComposer


class TestDeltaComposer:
    """Test delta composition and merging"""
    
    def test_init(self):
        """Test composer initialization"""
        composer = DeltaComposer()
        assert composer is not None
    
    def test_merge_deltas_equal_weights(self):
        """Test merging deltas with equal weights"""
        composer = DeltaComposer()
        
        delta_ids = ["delta_1", "delta_2"]
        
        result = composer.merge_deltas(delta_ids, orthogonalize=False)
        
        assert result["composed_id"] is not None
        assert result["source_deltas"] == delta_ids
        assert len(result["weights"]) == 2
        assert all(w == 0.5 for w in result["weights"])
    
    def test_merge_deltas_custom_weights(self):
        """Test merging with custom weights"""
        composer = DeltaComposer()
        
        delta_ids = ["delta_1", "delta_2", "delta_3"]
        weights = [0.5, 0.3, 0.2]
        
        result = composer.merge_deltas(delta_ids, weights=weights)
        
        assert result["weights"] == weights
    
    def test_merge_with_orthogonalization(self):
        """Test merging with orthogonalization"""
        composer = DeltaComposer()
        
        delta_ids = ["delta_1", "delta_2"]
        
        result = composer.merge_deltas(delta_ids, orthogonalize=True)
        
        assert result["orthogonalized"] is True
    
    def test_merge_weight_mismatch(self):
        """Test error on weight mismatch"""
        composer = DeltaComposer()
        
        delta_ids = ["delta_1", "delta_2"]
        weights = [0.5]  # Only one weight for two deltas
        
        with pytest.raises(ValueError):
            composer.merge_deltas(delta_ids, weights=weights)
    
    def test_estimated_regression(self):
        """Test regression estimation"""
        composer = DeltaComposer()
        
        delta_ids = ["delta_1", "delta_2"]
        result = composer.merge_deltas(delta_ids)
        
        assert "estimated_regression" in result
        assert isinstance(result["estimated_regression"], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
