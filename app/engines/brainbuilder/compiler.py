"""
Brain Compiler - Compile brain specs into deployable artifacts
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
import time

from .schemas import BrainSpec

logger = logging.getLogger(__name__)


class BrainCompiler:
    """
    Compile brain specifications into deployable artifacts:
    - Aura manifests
    - SkillPack bundles
    - Composite model manifests
    """
    
    def __init__(self, output_dir: str = "lab/brains/compiled"):
        """
        Initialize brain compiler.
        
        Args:
            output_dir: Directory for compiled artifacts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BrainCompiler initialized: {self.output_dir}")
    
    def compile(self, brain_spec: BrainSpec) -> Dict[str, Any]:
        """
        Compile a brain specification into deployable artifacts.
        
        Args:
            brain_spec: Validated brain specification
            
        Returns:
            Compilation results with artifact paths
        """
        logger.info(f"Compiling brain: {brain_spec.id}")
        
        artifacts = []
        
        # Generate composite manifest
        if brain_spec.adapter in ["aai_psm", "composite"]:
            manifest_path = self._compile_manifest(brain_spec)
            artifacts.append({
                "type": "manifest",
                "path": str(manifest_path)
            })
        
        # Generate Aura if defense is configured
        if brain_spec.defense:
            aura_path = self._compile_aura(brain_spec)
            artifacts.append({
                "type": "aura",
                "path": str(aura_path)
            })
        
        # Generate EPA SkillPack if seeds are specified
        if brain_spec.epa_seeds:
            skillpack_path = self._compile_skillpack(brain_spec)
            artifacts.append({
                "type": "skillpack",
                "path": str(skillpack_path)
            })
        
        results = {
            "brain_id": brain_spec.id,
            "status": "success",
            "artifacts": artifacts,
            "compiled_at": time.time()
        }
        
        logger.info(f"Brain compilation complete: {len(artifacts)} artifacts")
        return results
    
    def _compile_manifest(self, brain_spec: BrainSpec) -> Path:
        """
        Compile a model manifest from brain spec.
        
        Args:
            brain_spec: Brain specification
            
        Returns:
            Path to compiled manifest
        """
        manifest = {
            "id": brain_spec.id,
            "name": brain_spec.name,
            "adapter": brain_spec.adapter,
            "format": brain_spec.format,
            "defaults": brain_spec.defaults
        }
        
        # Add AAI configuration
        if brain_spec.aai:
            manifest["aai"] = brain_spec.aai.model_dump()
        
        # Add Induction configuration
        if brain_spec.induction:
            manifest["induction"] = brain_spec.induction
        
        # Write manifest
        manifest_path = self.output_dir / f"{brain_spec.id}_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Compiled manifest: {manifest_path}")
        return manifest_path
    
    def _compile_aura(self, brain_spec: BrainSpec) -> Path:
        """
        Compile a Defense Aura from brain spec.
        
        Args:
            brain_spec: Brain specification
            
        Returns:
            Path to compiled aura
        """
        aura = {
            "aura_id": f"{brain_spec.id}_defense",
            "name": f"{brain_spec.name} Defense",
            "type": "defense",
            "config": brain_spec.defense
        }
        
        aura_path = self.output_dir / f"{brain_spec.id}_aura.json"
        with open(aura_path, 'w') as f:
            json.dump(aura, f, indent=2)
        
        logger.info(f"Compiled aura: {aura_path}")
        return aura_path
    
    def _compile_skillpack(self, brain_spec: BrainSpec) -> Path:
        """
        Compile an EPA SkillPack from brain spec.
        
        Args:
            brain_spec: Brain specification
            
        Returns:
            Path to compiled skillpack
        """
        skillpack = {
            "skillpack_id": f"{brain_spec.id}_epa",
            "name": f"{brain_spec.name} EPA Skills",
            "type": "epa",
            "seeds": brain_spec.epa_seeds
        }
        
        skillpack_path = self.output_dir / f"{brain_spec.id}_skillpack.json"
        with open(skillpack_path, 'w') as f:
            json.dump(skillpack, f, indent=2)
        
        logger.info(f"Compiled skillpack: {skillpack_path}")
        return skillpack_path
