# OmniLoader

**Production-grade local-first AI model manager with dual-tab UI (Chat | Lab)**

OmniLoader is a comprehensive system for discovering, registering, and running ANY text-generation model locally. It features a dual-tab interface (Chat for daily use, Lab for advanced operations), supports multiple model backends, and includes advanced features like diagnostics, causal tracing, and live training.

## Features

### Core Features
- **Universal Model Support**: Works with GGUF/llama.cpp, HuggingFace Transformers, vLLM remote endpoints, ONNX Runtime, and custom backends
- **Dual-Tab UI**: Clean Streamlit interface with Chat and Lab tabs
- **Local-First**: Runs entirely on your machine, with optional remote connectors
- **Streaming Generation**: Real-time token streaming for responsive interactions
- **CPU-Optimized**: Default settings tuned for Windows 10 Home, i5-7200U, 16GB RAM

### Lab Features
- **Model Manager**: Load/unload models, view metadata
- **Diagnostics**: Comprehensive model X-ray (head roles, SAE features, capabilities, safety)
- **Trace & Target**: Causal localization and surgical interventions
- **Live Train**: Online learning with Hot-LoRA, DPO, and knowledge editing
- **Tokenizer**: Explore model tokenization
- **Artifacts**: Create and manage Auras, Snapshots, and SkillPacks

## Quick Start

### Prerequisites
- Python 3.8+
- Windows 10 or later
- 16GB RAM recommended

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/MASSIVEMAGNETICS/project-omni-omega.git
   cd project-omni-omega
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start the backend**
   ```bash
   run_backend.bat
   ```

3. **Start the UI** (new terminal)
   ```bash
   run_streamlit.bat
   ```

4. **Access**
   - UI: http://localhost:8501
   - API: http://localhost:8000/docs

## Architecture

```
app/
├── adapters/     # 5 model backends (llama.cpp, HF, vLLM, ONNX, Victor)
├── engines/      # Lab engines (diagnostics, trace, live_train)
├── registry/     # Model discovery and management
├── api/          # FastAPI routes
└── main.py       # Application entry

ui/
└── app.py        # Streamlit dual-tab UI

models/           # Model manifests (auto-discovered)
victor/           # Custom backend directory
lab/              # Lab artifacts storage
tests/            # Unit and integration tests
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
