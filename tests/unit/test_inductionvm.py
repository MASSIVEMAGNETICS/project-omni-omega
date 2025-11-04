"""
Tests for InductionVM components
"""
import pytest
import numpy as np

from app.engines.inductionvm import InductionIR, InductionScheduler, CPUKernels, KVCache
from app.engines.inductionvm.ir import OpType


class TestCPUKernels:
    """Test CPU kernel implementations"""
    
    def test_matmul(self):
        """Test matrix multiplication"""
        kernels = CPUKernels()
        
        a = np.array([[1, 2], [3, 4]], dtype=np.float32)
        b = np.array([[5, 6], [7, 8]], dtype=np.float32)
        
        result = kernels.matmul(a, b)
        expected = np.array([[19, 22], [43, 50]], dtype=np.float32)
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_add(self):
        """Test element-wise addition"""
        kernels = CPUKernels()
        
        a = np.array([1, 2, 3], dtype=np.float32)
        b = np.array([4, 5, 6], dtype=np.float32)
        
        result = kernels.add(a, b)
        expected = np.array([5, 7, 9], dtype=np.float32)
        
        np.testing.assert_array_equal(result, expected)
    
    def test_rmsnorm(self):
        """Test RMS normalization"""
        kernels = CPUKernels()
        
        x = np.array([[1, 2, 3, 4]], dtype=np.float32)
        weight = np.ones(4, dtype=np.float32)
        
        result = kernels.rmsnorm(x, weight)
        
        # Check that RMS is normalized
        rms = np.sqrt(np.mean(result ** 2))
        assert abs(rms - 1.0) < 0.1
    
    def test_softmax(self):
        """Test softmax operation"""
        kernels = CPUKernels()
        
        x = np.array([[1, 2, 3]], dtype=np.float32)
        result = kernels.softmax(x)
        
        # Check that sum is 1
        assert abs(np.sum(result) - 1.0) < 1e-5
        
        # Check that all values are positive
        assert np.all(result > 0)


class TestKVCache:
    """Test KV cache implementation"""
    
    def test_write_read(self):
        """Test writing and reading from cache"""
        cache = KVCache(num_layers=2, max_seq_len=10, hidden_dim=8, num_heads=2)
        
        # Write to cache
        k = np.ones((1, 3, 8), dtype=np.float32)
        v = np.ones((1, 3, 8), dtype=np.float32) * 2
        
        cache.write(0, k, v)
        
        # Read from cache
        k_read, v_read = cache.read(0)
        
        # Check shapes
        assert k_read.shape == (1, 3, 8)
        assert v_read.shape == (1, 3, 8)
        
        # Check values
        np.testing.assert_array_equal(k_read, k)
        np.testing.assert_array_equal(v_read, v)
    
    def test_clear(self):
        """Test clearing cache"""
        cache = KVCache(num_layers=2, max_seq_len=10)
        
        # Write to cache
        k = np.ones((1, 3, 4096), dtype=np.float32)
        v = np.ones((1, 3, 4096), dtype=np.float32)
        cache.write(0, k, v)
        
        # Clear
        cache.clear(0)
        
        # Check that cache is cleared
        assert cache.seq_lens[0] == 0


class TestInductionIR:
    """Test InductionVM IR"""
    
    def test_ir_construction(self):
        """Test building an IR graph"""
        ir = InductionIR()
        
        # Add tensors
        ir.add_tensor("x", [1, 10, 512])
        ir.add_tensor("w", [512, 512])
        ir.add_tensor("y", [1, 10, 512])
        
        # Add operation
        ir.matmul("x", "w", "y")
        
        # Check IR
        assert len(ir.nodes) == 1
        assert ir.nodes[0].op == OpType.MATMUL
        assert ir.nodes[0].inputs == ["x", "w"]
        assert ir.nodes[0].outputs == ["y"]


class TestInductionScheduler:
    """Test InductionVM scheduler"""
    
    def test_execute_simple(self):
        """Test executing a simple IR graph"""
        scheduler = InductionScheduler(num_layers=1, max_seq_len=10)
        
        # Build IR
        ir = InductionIR()
        ir.add_tensor("a", [2, 2])
        ir.add_tensor("b", [2, 2])
        ir.add_tensor("c", [2, 2])
        ir.add("a", "b", "c")
        
        # Prepare inputs
        inputs = {
            "a": np.array([[1, 2], [3, 4]], dtype=np.float32),
            "b": np.array([[5, 6], [7, 8]], dtype=np.float32)
        }
        
        # Execute
        outputs = scheduler.execute(ir, inputs)
        
        # Check result
        expected = np.array([[6, 8], [10, 12]], dtype=np.float32)
        np.testing.assert_array_equal(outputs["c"], expected)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
