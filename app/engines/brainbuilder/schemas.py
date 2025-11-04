"""
Brain Builder Schemas - Data models for brain specifications
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ToolConfig(BaseModel):
    """Tool configuration"""
    name: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


class ReflectionConfig(BaseModel):
    """Reflection/meta-cognition configuration"""
    enabled: bool = False
    budget_tokens: int = 128
    triggers: List[str] = Field(default_factory=list)


class MemoryConfig(BaseModel):
    """Memory system configuration"""
    vector_dim: int = 384
    k: int = 6
    persistence: bool = True


class AAIConfig(BaseModel):
    """Augmented AI configuration"""
    inner_manifest: Dict[str, Any]
    tools: List[str] = Field(default_factory=list)
    reflection: ReflectionConfig = Field(default_factory=ReflectionConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)


class BrainSpec(BaseModel):
    """
    Brain specification - declarative definition of an AI brain.
    Can be written in YAML or JSON.
    """
    id: str
    name: str
    description: str = ""
    adapter: str  # 'aai_psm', 'induction', 'composite', etc.
    format: str = "composite"
    
    # AAI/PSM configuration
    aai: Optional[AAIConfig] = None
    
    # InductionVM configuration
    induction: Optional[Dict[str, Any]] = None
    
    # Defense configuration
    defense: Optional[Dict[str, Any]] = None
    
    # EPA seeds
    epa_seeds: List[str] = Field(default_factory=list)
    
    # Default generation parameters
    defaults: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    version: str = "1.0"
