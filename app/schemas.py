"""
Schema definitions for model manifests and API requests/responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


class AdapterType(str, Enum):
    """Supported model adapter types"""
    LLAMA_CPP = "llama_cpp"
    HF_TRANSFORMERS = "hf_transformers"
    VLLM_REMOTE = "vllm_remote"
    ONNX_RUNTIME = "onnx_runtime"
    VICTOR_CUSTOM = "victor_custom"
    AAI_PSM = "aai_psm"
    INDUCTION = "induction"


class PromptTemplate(BaseModel):
    """Prompt template configuration"""
    system: Optional[str] = None
    chat: Optional[str] = None
    stop: Optional[List[str]] = None


class ModelFiles(BaseModel):
    """Model file paths"""
    weights: str
    tokenizer: Optional[str] = None
    config: Optional[str] = None


class ModelDefaults(BaseModel):
    """Default generation parameters"""
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 256
    threads: Optional[int] = 2


class LoRAConfig(BaseModel):
    """LoRA configuration"""
    enabled: bool = False
    paths: Optional[List[str]] = None


class ModelManifest(BaseModel):
    """Model manifest schema"""
    id: str
    name: str
    adapter: AdapterType
    files: ModelFiles
    format: Optional[str] = None
    dtype: Optional[str] = None
    context_length: int = 2048
    prompt_template: Optional[PromptTemplate] = None
    defaults: ModelDefaults = Field(default_factory=ModelDefaults)
    lora: Optional[LoRAConfig] = None
    metadata: Optional[Dict[str, Any]] = None


class GenerateRequest(BaseModel):
    """Request schema for text generation"""
    model_id: str
    prompt: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    stop: Optional[List[str]] = None
    stream: bool = True


class SessionRequest(BaseModel):
    """Request schema for chat session"""
    model_id: str
    system_prompt: Optional[str] = None


class SessionResponse(BaseModel):
    """Response schema for chat session"""
    session_id: str
    model_id: str


class ModelInfo(BaseModel):
    """Model information response"""
    id: str
    name: str
    adapter: str
    loaded: bool
    context_length: int
    defaults: ModelDefaults


class DiagnosticsRequest(BaseModel):
    """Request schema for diagnostics"""
    model_id: str
    modes: List[Literal["head_roles", "sae", "spectral", "capabilities", "redteam", "leakage"]]
    quick_mode: bool = True


class TraceRequest(BaseModel):
    """Request schema for causal tracing"""
    model_id: str
    prompt: str
    desired: Optional[str] = None
    methods: List[Literal["grad_act", "ig", "rollout"]] = ["grad_act"]
    resolution: List[Literal["layers", "heads", "mlp", "sae"]] = ["layers"]


class CausalTarget(BaseModel):
    """Target for causal intervention"""
    type: Literal["attn_head", "mlp", "residual"]
    layer: int
    head: Optional[int] = None


class CausalTestRequest(BaseModel):
    """Request schema for causal testing"""
    model_id: str
    prompt: str
    targets: List[CausalTarget]
    method: Literal["activation_patch", "ablate", "steer"]
    baseline_prompt: Optional[str] = None


class TrainTargetRequest(BaseModel):
    """Request schema for targeted training"""
    model_id: str
    strategy: Literal["bias", "lora", "feature", "rome"]
    targets: List[CausalTarget]
    params: Dict[str, Any]
    dataset: Dict[str, Any]
    aura_id: Optional[str] = None


class LiveTrainRequest(BaseModel):
    """Request schema for live training"""
    model_id: str
    mode: Literal["rule", "hot_lora", "dpo", "rome"]
    budget: Dict[str, Any]
    dataset: Optional[Dict[str, Any]] = None


class SnapshotRequest(BaseModel):
    """Request schema for creating snapshots"""
    model_id: str
    description: Optional[str] = None


class AuraRequest(BaseModel):
    """Request schema for aura operations"""
    aura_id: Optional[str] = None
    name: str
    model_id: str
    components: Dict[str, Any]


class SkillPackRequest(BaseModel):
    """Request schema for skillpack export"""
    name: str
    model_id: str
    include_dataset: bool = True
    include_deltas: bool = True
    include_evals: bool = True


class QueueExample(BaseModel):
    """Example for training queue"""
    prompt: str
    chosen: str
    rejected: Optional[str] = None
    tags: Optional[List[str]] = None
    aura_id: Optional[str] = None
