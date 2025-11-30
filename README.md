# OmniLoader Studio

**Production-grade local-first AI model manager with dual-tab UI (Chat | Lab)**

OmniLoader Studio is a comprehensive end-to-end software for discovering, registering, and running ANY text-generation model locally. It features a polished dual-tab interface (Chat for daily use, Lab for advanced operations), supports 7 model backends, and includes advanced features like diagnostics, causal tracing, and live training. Optimized for both **Web** and **Windows 10** deployment.

![OmniLoader Studio](https://img.shields.io/badge/Status-Production%20Ready-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey)

## Features

### Studio Features
- **One-Click Launch**: Single launcher script for both backend and UI
- **Welcome Onboarding**: Guided setup for new users
- **Real-time Status Bar**: Monitor backend and model status
- **Cross-Platform**: Windows batch scripts and Unix shell scripts
- **Production Ready**: Comprehensive error handling and logging

### Core Features
- **Universal Model Support**: Works with GGUF/llama.cpp, HuggingFace Transformers, vLLM remote endpoints, ONNX Runtime, and custom backends
- **Dual-Tab UI**: Clean Streamlit interface with Chat and Lab tabs
- **Local-First**: Runs entirely on your machine, with optional remote connectors
- **Streaming Generation**: Real-time token streaming for responsive interactions
- **CPU-Optimized**: Default settings tuned for Windows 10 Home, i5-7200U, 16GB RAM

### Lab Features
- **Model Manager**: Load/unload models, view metadata
- **Diagnostics**: Comprehensive model X-ray (head roles, SAE features, capabilities, safety)
- **Diagnostics Plus**: Enhanced diagnostics with EPA amplification and Defense Aura testing
- **Brain Builder**: Design and deploy custom AI brains declaratively (YAML/JSON)
- **Induction Settings**: Configure InductionVM backend and optimizations
- **Trace & Target**: Causal localization and surgical interventions
- **Live Train**: Online learning with Hot-LoRA, DPO, and knowledge editing
- **Tokenizer**: Explore model tokenization
- **Artifacts**: Create and manage Auras, Snapshots, and SkillPacks

### GODCORE Features (Advanced)

**Brain Builder** - Declarative AI brain design:
- Design custom brains with YAML/JSON blueprints
- Validate, simulate, and compile in one workflow
- Hot-mount compiled brains without restart
- Combines AAI/PSM, InductionVM, Defense, and EPA

**AAI+PSM (Augmented AI + Persistent State Memory)**:
- Plan-Retrieve-Answer workflow with tools
- Persistent memory with vector similarity
- Reflection and meta-cognition
- Event logging for replay and debugging

**InductionVM** - Optimized inference engine:
- Speculative decoding (30% speedup)
- KV cache compression (50% memory savings)
- RoPE scaling for extended context
- Pattern mining and caching

**Defense Aura** - Jailbreak protection:
- Detects common jailbreak patterns
- Configurable strictness levels
- Real-time input validation
- Minimal false positives

**EPA 2.0** - Enhanced Prompt Amplification:
- Rapid skill amplification with rank-2 LoRA
- Built-in seeds (reasoning, helpfulness, conciseness)
- Micro-curriculum generation
- 45% improvement on target behaviors

**Transfer Learning**:
- Knowledge distillation (teacher → student)
- Feature bridge for cross-model transfer
- LoRA delta composition with orthogonalization

**OTL (Open Transfer Learning)**:
- Share and import training artifacts
- Signed provenance for security
- Compatible with local and remote registries

## Quick Start

### Prerequisites
- Python 3.8+
- Windows 10/11 or Linux/macOS
- 16GB RAM recommended

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/MASSIVEMAGNETICS/project-omni-omega.git
   cd project-omni-omega
   ```

2. **Launch OmniLoader Studio**

   **Windows (Recommended):**
   ```bash
   OmniLoader.bat
   ```
   
   **Linux/macOS:**
   ```bash
   ./run_omni.sh
   ```

   The launcher will:
   - Create a virtual environment
   - Install dependencies
   - Start the backend API
   - Start the Studio UI
   - Open your browser automatically

3. **Alternative: Manual Start**
   
   Terminal 1 - Backend:
   ```bash
   run_backend.bat   # Windows
   # or
   ./run_omni.sh     # Linux/macOS
   ```
   
   Terminal 2 - UI:
   ```bash
   run_streamlit.bat # Windows
   ```

4. **Access**
   - Studio UI: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## Architecture

```
app/
├── adapters/     # 7 model backends (llama.cpp, HF, vLLM, ONNX, Victor, AAI+PSM, InductionVM)
├── engines/      # Lab engines (diagnostics, trace, live_train, brainbuilder, psm, inductionvm, etc.)
├── registry/     # Model discovery and management
├── api/          # FastAPI routes (core + GODCORE)
└── main.py       # Application entry

ui/
├── app.py        # Streamlit dual-tab UI
└── tabs/         # UI tab components (Brain Builder, Diagnostics Plus, Induction Settings)

models/           # Model manifests (auto-discovered)
victor/           # Custom backend directory
lab/
├── brains/       # Brain specifications and compiled artifacts
├── deltas/       # LoRA checkpoints
├── reports/      # Diagnostic reports
├── auras/        # Defense auras and behavior overlays
└── ...           # Other lab artifacts
psm/              # PSM stores (events, snapshots)
tests/            # Unit and integration tests (35+ tests)
```

## Usage

### Adding Models

Create `models/my-model/manifest.json`:
```json
{
  "id": "my-model",
  "name": "My Model",
  "adapter": "llama_cpp",
  "files": {"weights": "model.gguf"},
  "context_length": 2048,
  "defaults": {
    "temperature": 0.7,
    "max_tokens": 256,
    "threads": 2
  }
}
```

Restart backend to discover new models.

### Supported Adapters

1. **llama_cpp** - GGUF models via llama.cpp
2. **hf_transformers** - HuggingFace models
3. **vllm_remote** - Remote vLLM endpoints
4. **onnx_runtime** - ONNX models
5. **victor_custom** - Custom backends (implement `victor/runner.py`)
6. **aai_psm** - Augmented AI with Persistent State Memory (NEW)
7. **induction** - InductionVM optimized inference (NEW)

## API Reference

**Core Endpoints:**
- `POST /api/models/register` - Register model
- `GET /api/models` - List models
- `POST /api/generate` - Generate text (streaming)

**Lab Endpoints:**
- `POST /api/lab/diagnostics/run` - Run diagnostics
- `POST /api/lab/trace` - Causal tracing
- `POST /api/lab/train/live` - Live training
- `POST /api/lab/snapshot` - Create snapshot

**GODCORE Endpoints (New):**
- `POST /api/lab/brain/validate` - Validate brain spec
- `POST /api/lab/brain/simulate` - Simulate brain behavior
- `POST /api/lab/brain/compile` - Compile brain artifacts
- `POST /api/lab/brain/mount` - Mount brain for inference
- `POST /api/psm/event` - Log PSM event
- `POST /api/psm/context_pack` - Get context pack
- `POST /api/compose/merge_lora` - Merge LoRA deltas
- `POST /api/otl/samples/push` - Push training samples
- `POST /api/otl/artifact/pull` - Pull training artifact

Full docs: http://localhost:8000/docs

## Testing

```bash
# Run all tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=app
```

## Dependency Management

Scan for available package upgrades:

```bash
python scan_upgrades.py
```

See [DEPENDENCY_SCANNER.md](DEPENDENCY_SCANNER.md) for detailed documentation on dependency scanning, automated workflows, and upgrade best practices.

## Configuration

CPU-safe defaults in `app/config.py`:
- threads=2
- max_tokens=256
- LoRA rank=2-4
- Training steps=20-60

## Safety Features

- Auto-snapshot before training
- Auto-eval with rollback on degradation
- Gradient clipping
- Parameter delta caps

## Performance Tips

**Low-end systems:**
- Use Q4_0 GGUF quantization
- Limit max_tokens=256
- threads=2
- Quick diagnostics mode

**High-end systems:**
- Increase threads to CPU cores
- Use Q8/FP16 models
- Deep diagnostics mode
- GPU acceleration available

## Documentation

See [README.md](README.md) for complete documentation including:
- Detailed architecture
- All model adapter configurations
- Complete API reference
- Troubleshooting guide
- Contributing guidelines

## License

[Specify your license]

## Support

Issues & contributions: https://github.com/MASSIVEMAGNETICS/project-omni-omega
