"""
Configuration settings for OmniLoader
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "OmniLoader API"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Paths
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir: str = os.path.join(base_dir, "models")
    victor_dir: str = os.path.join(base_dir, "victor")
    lab_dir: str = os.path.join(base_dir, "lab")
    
    # CPU-safe defaults for Windows 10 Home, i5-7200U, 16GB RAM
    default_threads: int = 2
    default_max_tokens: int = 256
    default_temperature: float = 0.7
    default_top_p: float = 0.9
    
    # Training defaults (CPU-safe)
    default_lora_rank: int = 2
    default_lora_steps: int = 40
    default_lora_lr: float = 2e-4
    default_lora_max_modules: int = 4
    
    # DPO/KTO defaults
    default_dpo_pairs: int = 8
    default_dpo_steps: int = 30
    
    # Diagnostics
    diagnostics_quick_timeout: int = 150  # seconds
    
    # Safety
    auto_snapshot: bool = True
    auto_eval: bool = True
    max_grad_norm: float = 1.0
    max_param_delta_l2: float = 0.5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
