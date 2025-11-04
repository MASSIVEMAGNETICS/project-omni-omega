"""
EPA Seeds - Seed behaviors for amplification
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class EPASeeds:
    """
    Manage EPA seed behaviors for targeted skill amplification.
    Seeds are small example sets that define behaviors to amplify.
    """
    
    def __init__(self):
        self.seeds: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("EPASeeds initialized")
    
    def add_seed(self, seed_id: str, examples: List[Dict[str, Any]], 
                 description: str = ""):
        """
        Add a seed behavior.
        
        Args:
            seed_id: Unique seed identifier
            examples: List of example inputs/outputs
            description: Seed description
        """
        self.seeds[seed_id] = {
            "examples": examples,
            "description": description,
            "created_at": None  # Would be timestamp in production
        }
        logger.info(f"Added EPA seed: {seed_id} with {len(examples)} examples")
    
    def get_seed(self, seed_id: str) -> Dict[str, Any]:
        """Get a seed by ID"""
        return self.seeds.get(seed_id)
    
    def list_seeds(self) -> List[str]:
        """List all seed IDs"""
        return list(self.seeds.keys())
    
    def get_builtin_seeds(self) -> Dict[str, Dict[str, Any]]:
        """
        Get built-in EPA seeds for common capabilities.
        
        Returns:
            Dictionary of built-in seeds
        """
        builtins = {
            "reasoning": {
                "description": "Chain-of-thought reasoning",
                "examples": [
                    {
                        "prompt": "What is 15% of 80?",
                        "chosen": "Let me work through this step by step:\n1. 15% = 15/100 = 0.15\n2. 0.15 × 80 = 12\nThe answer is 12.",
                        "rejected": "The answer is 12."
                    },
                    {
                        "prompt": "If a train travels at 60 mph for 2.5 hours, how far does it go?",
                        "chosen": "To find distance, I'll use: distance = speed × time\n- Speed = 60 mph\n- Time = 2.5 hours\n- Distance = 60 × 2.5 = 150 miles\nThe train travels 150 miles.",
                        "rejected": "150 miles."
                    }
                ]
            },
            "helpfulness": {
                "description": "Comprehensive, helpful responses",
                "examples": [
                    {
                        "prompt": "How do I learn Python?",
                        "chosen": "Here's a structured approach to learning Python:\n1. Start with basics (variables, data types, control flow)\n2. Practice with small projects\n3. Learn standard libraries\n4. Build real applications\n5. Contribute to open source\n\nRecommended resources: Python.org tutorial, Automate the Boring Stuff, Real Python.",
                        "rejected": "Read some tutorials and practice coding."
                    }
                ]
            },
            "conciseness": {
                "description": "Concise, direct responses",
                "examples": [
                    {
                        "prompt": "What is the capital of France?",
                        "chosen": "Paris.",
                        "rejected": "The capital of France is a beautiful city known for its art, culture, and history. It is called Paris, and it's located in the north-central part of the country."
                    }
                ]
            }
        }
        return builtins
    
    def generate_micro_curriculum(self, seed_id: str, 
                                  num_synthetic: int = 20) -> List[Dict[str, Any]]:
        """
        Generate a micro-curriculum from a seed.
        
        Creates synthetic variations of seed examples for training.
        
        Args:
            seed_id: Seed to expand
            num_synthetic: Number of synthetic examples to generate
            
        Returns:
            Expanded training curriculum
        """
        seed = self.get_seed(seed_id)
        if not seed:
            raise ValueError(f"Seed not found: {seed_id}")
        
        examples = seed["examples"]
        curriculum = list(examples)  # Start with original examples
        
        # Generate synthetic variations
        # In production, this would use:
        # - Paraphrasing
        # - Template-based generation
        # - Back-translation
        # - Constrastive examples
        
        logger.info(f"Generated micro-curriculum for {seed_id}: "
                   f"{len(examples)} base + {num_synthetic} synthetic")
        
        # Placeholder: just duplicate for now
        curriculum.extend(examples[:num_synthetic])
        
        return curriculum
