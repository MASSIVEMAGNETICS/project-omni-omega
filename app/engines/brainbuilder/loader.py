"""
Brain Loader - Load and validate brain specifications
"""
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Union

from .schemas import BrainSpec

logger = logging.getLogger(__name__)


class BrainLoader:
    """
    Load brain specifications from YAML or JSON files.
    Validates against the BrainSpec schema.
    """
    
    def __init__(self, brains_dir: str = "lab/brains"):
        """
        Initialize brain loader.
        
        Args:
            brains_dir: Directory containing brain specifications
        """
        self.brains_dir = Path(brains_dir)
        self.brains_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BrainLoader initialized: {self.brains_dir}")
    
    def load(self, spec_path: Union[str, Path]) -> BrainSpec:
        """
        Load a brain specification from file.
        
        Args:
            spec_path: Path to YAML or JSON file
            
        Returns:
            Validated BrainSpec object
        """
        spec_path = Path(spec_path)
        
        if not spec_path.exists():
            raise FileNotFoundError(f"Brain spec not found: {spec_path}")
        
        logger.info(f"Loading brain spec: {spec_path}")
        
        # Load file content
        with open(spec_path, 'r') as f:
            if spec_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif spec_path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {spec_path.suffix}")
        
        # Validate and parse
        try:
            brain_spec = BrainSpec(**data)
            logger.info(f"Successfully loaded brain: {brain_spec.id}")
            return brain_spec
        except Exception as e:
            logger.error(f"Failed to validate brain spec: {e}")
            raise
    
    def load_from_dict(self, spec_dict: Dict[str, Any]) -> BrainSpec:
        """
        Load a brain specification from dictionary.
        
        Args:
            spec_dict: Brain specification dictionary
            
        Returns:
            Validated BrainSpec object
        """
        try:
            brain_spec = BrainSpec(**spec_dict)
            return brain_spec
        except Exception as e:
            logger.error(f"Failed to validate brain spec: {e}")
            raise
    
    def validate(self, spec: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a brain specification.
        
        Args:
            spec: Path to file or dictionary
            
        Returns:
            Validation results
        """
        try:
            if isinstance(spec, dict):
                brain_spec = self.load_from_dict(spec)
            else:
                brain_spec = self.load(spec)
            
            return {
                "valid": True,
                "brain_id": brain_spec.id,
                "adapter": brain_spec.adapter,
                "issues": []
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "issues": [str(e)]
            }
    
    def list_brains(self) -> list:
        """
        List all brain specifications in the brains directory.
        
        Returns:
            List of brain spec file paths
        """
        brains = []
        for ext in ['*.yaml', '*.yml', '*.json']:
            brains.extend(self.brains_dir.glob(ext))
        return brains
