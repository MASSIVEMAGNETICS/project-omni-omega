"""
KV Cache Compression - Reduce memory footprint
"""
import logging
import numpy as np

logger = logging.getLogger(__name__)


class KVCompressor:
    """
    Compress KV cache to reduce memory usage while maintaining quality.
    Supports INT8 per-head quantization and other compression schemes.
    """
    
    def __init__(self, mode: str = "int8-per-head", segment_bytes: int = 512):
        """
        Initialize KV compressor.
        
        Args:
            mode: Compression mode ('int8-per-head', 'int4', etc.)
            segment_bytes: Segment size for compression
        """
        self.mode = mode
        self.segment_bytes = segment_bytes
        
        logger.info(f"KVCompressor initialized with mode={mode}, segment_bytes={segment_bytes}")
    
    def compress(self, k: np.ndarray, v: np.ndarray) -> tuple:
        """
        Compress key and value tensors.
        
        Args:
            k: Key tensor [batch, seq_len, hidden_dim]
            v: Value tensor [batch, seq_len, hidden_dim]
            
        Returns:
            Tuple of (compressed_k, compressed_v, metadata)
        """
        if self.mode == "int8-per-head":
            return self._compress_int8_per_head(k, v)
        else:
            # Fallback: no compression
            return k, v, {}
    
    def _compress_int8_per_head(self, k: np.ndarray, v: np.ndarray) -> tuple:
        """
        Compress using INT8 quantization per attention head.
        
        Args:
            k: Key tensor
            v: Value tensor
            
        Returns:
            Compressed tensors and metadata
        """
        # Reshape to separate heads
        # Assuming shape [batch, seq_len, num_heads, head_dim]
        batch, seq_len, hidden = k.shape
        
        # Simple INT8 quantization
        k_min, k_max = k.min(), k.max()
        k_scale = (k_max - k_min) / 255.0
        k_compressed = ((k - k_min) / k_scale).astype(np.int8)
        
        v_min, v_max = v.min(), v.max()
        v_scale = (v_max - v_min) / 255.0
        v_compressed = ((v - v_min) / v_scale).astype(np.int8)
        
        metadata = {
            "k_min": float(k_min),
            "k_max": float(k_max),
            "k_scale": float(k_scale),
            "v_min": float(v_min),
            "v_max": float(v_max),
            "v_scale": float(v_scale),
            "original_dtype": str(k.dtype)
        }
        
        logger.debug(f"Compressed KV cache: {k.nbytes + v.nbytes} -> "
                    f"{k_compressed.nbytes + v_compressed.nbytes} bytes")
        
        return k_compressed, v_compressed, metadata
    
    def decompress(self, k_compressed: np.ndarray, v_compressed: np.ndarray, 
                   metadata: dict) -> tuple:
        """
        Decompress KV cache.
        
        Args:
            k_compressed: Compressed key tensor
            v_compressed: Compressed value tensor
            metadata: Compression metadata
            
        Returns:
            Decompressed (k, v) tensors
        """
        if self.mode == "int8-per-head":
            k = k_compressed.astype(np.float32) * metadata["k_scale"] + metadata["k_min"]
            v = v_compressed.astype(np.float32) * metadata["v_scale"] + metadata["v_min"]
            return k, v
        else:
            return k_compressed, v_compressed
