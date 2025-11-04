"""
InductionVM CPU Kernels - Optimized operations
"""
import numpy as np
from typing import Tuple


class CPUKernels:
    """
    CPU-optimized kernels for InductionVM operations
    """
    
    def matmul(self, x: np.ndarray, w: np.ndarray) -> np.ndarray:
        """
        Matrix multiplication.
        
        Args:
            x: Input tensor
            w: Weight tensor
            
        Returns:
            Output tensor
        """
        return np.matmul(x, w)
    
    def add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Element-wise addition"""
        return a + b
    
    def mul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Element-wise multiplication"""
        return a * b
    
    def rmsnorm(self, x: np.ndarray, weight: np.ndarray, eps: float = 1e-6) -> np.ndarray:
        """
        RMS normalization.
        
        Args:
            x: Input tensor
            weight: Scale weights
            eps: Epsilon for numerical stability
            
        Returns:
            Normalized tensor
        """
        variance = np.mean(x ** 2, axis=-1, keepdims=True)
        x_normed = x / np.sqrt(variance + eps)
        return x_normed * weight
    
    def softmax(self, x: np.ndarray, dim: int = -1) -> np.ndarray:
        """
        Softmax operation.
        
        Args:
            x: Input tensor
            dim: Dimension to apply softmax
            
        Returns:
            Softmax output
        """
        x_max = np.max(x, axis=dim, keepdims=True)
        exp_x = np.exp(x - x_max)
        return exp_x / np.sum(exp_x, axis=dim, keepdims=True)
    
    def rope_apply(self, q: np.ndarray, k: np.ndarray, position: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply Rotary Position Embedding (RoPE).
        
        Args:
            q: Query tensor
            k: Key tensor
            position: Position index
            
        Returns:
            Rotated (q, k) tensors
        """
        # Simplified RoPE implementation
        # In production, this would use proper frequency computation
        def rotate_half(x):
            x1, x2 = np.split(x, 2, axis=-1)
            return np.concatenate([-x2, x1], axis=-1)
        
        # Simple rotation based on position
        theta = position * 0.0001  # Simplified frequency
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        q_rot = q * cos_theta + rotate_half(q) * sin_theta
        k_rot = k * cos_theta + rotate_half(k) * sin_theta
        
        return q_rot, k_rot
