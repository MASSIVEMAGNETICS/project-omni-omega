"""
Feature Bridge - Map features between model architectures
"""
import logging
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FeatureBridge:
    """
    Map feature representations between different model architectures.
    Enables cross-model skill transfer by learning direction mappings.
    """
    
    def __init__(self, source_dim: int, target_dim: int):
        """
        Initialize feature bridge.
        
        Args:
            source_dim: Source model hidden dimension
            target_dim: Target model hidden dimension
        """
        self.source_dim = source_dim
        self.target_dim = target_dim
        self.projection = None
        
        logger.info(f"FeatureBridge initialized: {source_dim} -> {target_dim}")
    
    def learn_mapping(self, source_features: np.ndarray, 
                     target_features: np.ndarray) -> Dict[str, Any]:
        """
        Learn a mapping from source to target feature space.
        
        Args:
            source_features: Features from source model [n_samples, source_dim]
            target_features: Features from target model [n_samples, target_dim]
            
        Returns:
            Mapping results
        """
        logger.info("Learning feature mapping...")
        
        # Simple linear projection via least squares
        # In production, this could use more sophisticated methods:
        # - Procrustes alignment
        # - CCA (Canonical Correlation Analysis)
        # - Neural mapping networks
        
        if source_features.shape[0] != target_features.shape[0]:
            raise ValueError("Source and target features must have same number of samples")
        
        # Compute projection matrix: W such that source @ W ≈ target
        self.projection = np.linalg.lstsq(source_features, target_features, rcond=None)[0]
        
        # Compute reconstruction error
        predicted = source_features @ self.projection
        mse = np.mean((predicted - target_features) ** 2)
        
        results = {
            "projection_shape": self.projection.shape,
            "reconstruction_mse": float(mse),
            "status": "success"
        }
        
        logger.info(f"Feature mapping learned: MSE={mse:.6f}")
        return results
    
    def map_features(self, source_features: np.ndarray) -> np.ndarray:
        """
        Map source features to target space.
        
        Args:
            source_features: Features from source model
            
        Returns:
            Mapped features in target space
        """
        if self.projection is None:
            raise ValueError("Feature mapping not learned yet")
        
        return source_features @ self.projection
    
    def map_direction(self, source_direction: np.ndarray) -> np.ndarray:
        """
        Map a direction vector from source to target space.
        Useful for transferring LoRA deltas or steering vectors.
        
        Args:
            source_direction: Direction in source space
            
        Returns:
            Mapped direction in target space
        """
        if self.projection is None:
            raise ValueError("Feature mapping not learned yet")
        
        # Normalize direction
        source_norm = source_direction / (np.linalg.norm(source_direction) + 1e-8)
        
        # Map and re-normalize
        target_direction = source_norm @ self.projection
        target_norm = target_direction / (np.linalg.norm(target_direction) + 1e-8)
        
        return target_norm
    
    def save(self, path: str):
        """Save feature bridge to file"""
        if self.projection is not None:
            np.save(path, self.projection)
            logger.info(f"Feature bridge saved to {path}")
    
    def load(self, path: str):
        """Load feature bridge from file"""
        self.projection = np.load(path)
        logger.info(f"Feature bridge loaded from {path}")
