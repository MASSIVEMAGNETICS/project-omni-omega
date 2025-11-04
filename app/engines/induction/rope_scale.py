"""
RoPE Scaler - Scale context length with YaRN/NTK methods
"""
import logging
import numpy as np

logger = logging.getLogger(__name__)


class RoPEScaler:
    """
    Scale Rotary Position Embeddings to extend context length.
    Supports YaRN (Yet another RoPE extensioN) and NTK-aware scaling.
    """
    
    def __init__(self, mode: str = "yarn", factor: float = 1.3):
        """
        Initialize RoPE scaler.
        
        Args:
            mode: Scaling mode ('yarn', 'ntk', 'linear')
            factor: Scaling factor (>1.0 extends context)
        """
        self.mode = mode
        self.factor = factor
        
        logger.info(f"RoPEScaler initialized with mode={mode}, factor={factor}")
    
    def scale_frequencies(self, freqs: np.ndarray, max_position: int) -> np.ndarray:
        """
        Scale RoPE frequencies for extended context.
        
        Args:
            freqs: Original RoPE frequencies
            max_position: Maximum position to support
            
        Returns:
            Scaled frequencies
        """
        if self.mode == "yarn":
            return self._yarn_scale(freqs, max_position)
        elif self.mode == "ntk":
            return self._ntk_scale(freqs, max_position)
        elif self.mode == "linear":
            return freqs / self.factor
        else:
            return freqs
    
    def _yarn_scale(self, freqs: np.ndarray, max_position: int) -> np.ndarray:
        """
        YaRN scaling method.
        
        YaRN applies different scaling factors to different frequency bands,
        preserving high-frequency information while extending low frequencies.
        """
        # Simplified YaRN implementation
        # In production, this would use proper wavelength-based scaling
        
        # Low frequencies (long wavelengths) get more scaling
        # High frequencies (short wavelengths) get less scaling
        dim = len(freqs)
        scale_factors = np.linspace(1.0, self.factor, dim)
        
        return freqs / scale_factors
    
    def _ntk_scale(self, freqs: np.ndarray, max_position: int) -> np.ndarray:
        """
        NTK-aware scaling method.
        
        Neural Tangent Kernel aware interpolation adjusts the base
        frequency instead of linearly interpolating positions.
        """
        # NTK scaling adjusts the base rather than the positions
        base_adjustment = self.factor ** (1.0 / len(freqs))
        return freqs / base_adjustment
    
    def compute_scaled_rope(self, dim: int, max_position: int, base: float = 10000.0) -> np.ndarray:
        """
        Compute scaled RoPE embeddings.
        
        Args:
            dim: Embedding dimension
            max_position: Maximum position
            base: RoPE base frequency
            
        Returns:
            Scaled RoPE embeddings
        """
        # Compute base frequencies
        freqs = 1.0 / (base ** (np.arange(0, dim, 2).astype(np.float32) / dim))
        
        # Scale frequencies
        scaled_freqs = self.scale_frequencies(freqs, max_position)
        
        # Compute position embeddings
        positions = np.arange(max_position)
        emb = np.outer(positions, scaled_freqs)
        
        # Return cos and sin components
        cos_emb = np.cos(emb)
        sin_emb = np.sin(emb)
        
        return np.stack([cos_emb, sin_emb], axis=-1)
