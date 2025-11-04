"""
Pattern Miner - Discover and cache common patterns
"""
import logging
from typing import List, Dict, Any
from collections import Counter

logger = logging.getLogger(__name__)


class PatternMiner:
    """
    Mine common patterns in model inputs/outputs for caching and optimization.
    Identifies repeated sequences that can be cached or optimized.
    """
    
    def __init__(self, min_frequency: int = 3, max_pattern_length: int = 10):
        """
        Initialize pattern miner.
        
        Args:
            min_frequency: Minimum frequency to consider a pattern
            max_pattern_length: Maximum length of patterns to mine
        """
        self.min_frequency = min_frequency
        self.max_pattern_length = max_pattern_length
        self.patterns: Dict[tuple, int] = Counter()
        
        logger.info(f"PatternMiner initialized with min_freq={min_frequency}, "
                   f"max_len={max_pattern_length}")
    
    def observe(self, sequence: List[Any]):
        """
        Observe a sequence and update pattern statistics.
        
        Args:
            sequence: Input sequence (tokens, activations, etc.)
        """
        seq_len = len(sequence)
        
        # Extract patterns of various lengths
        for length in range(2, min(self.max_pattern_length + 1, seq_len + 1)):
            for i in range(seq_len - length + 1):
                pattern = tuple(sequence[i:i+length])
                self.patterns[pattern] += 1
    
    def get_frequent_patterns(self, top_k: int = 10) -> List[tuple]:
        """
        Get most frequent patterns.
        
        Args:
            top_k: Number of top patterns to return
            
        Returns:
            List of (pattern, frequency) tuples
        """
        # Filter by minimum frequency
        frequent = [(p, f) for p, f in self.patterns.items() 
                   if f >= self.min_frequency]
        
        # Sort by frequency
        frequent.sort(key=lambda x: x[1], reverse=True)
        
        return frequent[:top_k]
    
    def is_cacheable(self, sequence: List[Any]) -> bool:
        """
        Check if a sequence contains cacheable patterns.
        
        Args:
            sequence: Input sequence
            
        Returns:
            True if sequence contains frequent patterns
        """
        seq_len = len(sequence)
        
        for length in range(2, min(self.max_pattern_length + 1, seq_len + 1)):
            for i in range(seq_len - length + 1):
                pattern = tuple(sequence[i:i+length])
                if pattern in self.patterns and self.patterns[pattern] >= self.min_frequency:
                    return True
        
        return False
    
    def get_pattern_cache_key(self, sequence: List[Any]) -> str:
        """
        Generate a cache key for a sequence based on its patterns.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Cache key string
        """
        # Find the longest matching pattern
        best_pattern = None
        best_length = 0
        
        seq_len = len(sequence)
        for length in range(2, min(self.max_pattern_length + 1, seq_len + 1)):
            for i in range(seq_len - length + 1):
                pattern = tuple(sequence[i:i+length])
                if (pattern in self.patterns and 
                    self.patterns[pattern] >= self.min_frequency and 
                    length > best_length):
                    best_pattern = pattern
                    best_length = length
        
        if best_pattern:
            return f"pattern_{hash(best_pattern)}"
        else:
            return f"seq_{hash(tuple(sequence))}"
    
    def clear(self):
        """Clear all observed patterns"""
        self.patterns.clear()
        logger.info("Pattern cache cleared")
