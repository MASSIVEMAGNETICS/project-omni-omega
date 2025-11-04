"""
InductionVM KV Cache - Key-Value cache for attention
"""
import numpy as np
from typing import Tuple, Optional


class KVCache:
    """
    Key-Value cache for transformer attention layers
    """
    
    def __init__(self, num_layers: int, max_seq_len: int, 
                 hidden_dim: int = 4096, num_heads: int = 32):
        """
        Initialize KV cache.
        
        Args:
            num_layers: Number of transformer layers
            max_seq_len: Maximum sequence length
            hidden_dim: Hidden dimension size
            num_heads: Number of attention heads
        """
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        # Initialize cache storage
        self.k_cache = {}
        self.v_cache = {}
        self.seq_lens = {}
        
        for layer in range(num_layers):
            self.k_cache[layer] = None
            self.v_cache[layer] = None
            self.seq_lens[layer] = 0
    
    def write(self, layer: int, k: np.ndarray, v: np.ndarray):
        """
        Write key and value tensors to cache.
        
        Args:
            layer: Layer index
            k: Key tensor [batch, seq_len, hidden_dim]
            v: Value tensor [batch, seq_len, hidden_dim]
        """
        if self.k_cache[layer] is None:
            # Initialize cache for this layer
            batch_size = k.shape[0]
            cache_shape = (batch_size, self.max_seq_len, k.shape[-1])
            self.k_cache[layer] = np.zeros(cache_shape, dtype=k.dtype)
            self.v_cache[layer] = np.zeros(cache_shape, dtype=v.dtype)
        
        # Append to cache
        seq_len = k.shape[1]
        start_pos = self.seq_lens[layer]
        end_pos = start_pos + seq_len
        
        self.k_cache[layer][:, start_pos:end_pos, :] = k
        self.v_cache[layer][:, start_pos:end_pos, :] = v
        self.seq_lens[layer] = end_pos
    
    def read(self, layer: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Read key and value tensors from cache.
        
        Args:
            layer: Layer index
            
        Returns:
            Tuple of (k, v) tensors
        """
        if self.k_cache[layer] is None:
            raise ValueError(f"Cache not initialized for layer {layer}")
        
        seq_len = self.seq_lens[layer]
        k = self.k_cache[layer][:, :seq_len, :]
        v = self.v_cache[layer][:, :seq_len, :]
        
        return k, v
    
    def compress(self, layer: int, mode: str = "int8"):
        """
        Compress KV cache to reduce memory.
        
        Args:
            layer: Layer index
            mode: Compression mode ('int8', 'int4', etc.)
        """
        if mode == "int8":
            if self.k_cache[layer] is not None:
                # Simple INT8 quantization
                k = self.k_cache[layer]
                k_min, k_max = k.min(), k.max()
                k_scale = (k_max - k_min) / 255.0
                self.k_cache[layer] = ((k - k_min) / k_scale).astype(np.int8)
                
                v = self.v_cache[layer]
                v_min, v_max = v.min(), v.max()
                v_scale = (v_max - v_min) / 255.0
                self.v_cache[layer] = ((v - v_min) / v_scale).astype(np.int8)
    
    def clear(self, layer: Optional[int] = None):
        """
        Clear cache for a layer or all layers.
        
        Args:
            layer: Layer index, or None to clear all
        """
        if layer is not None:
            self.k_cache[layer] = None
            self.v_cache[layer] = None
            self.seq_lens[layer] = 0
        else:
            for l in range(self.num_layers):
                self.k_cache[l] = None
                self.v_cache[l] = None
                self.seq_lens[l] = 0
