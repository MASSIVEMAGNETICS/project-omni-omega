# OmniLoader Quick Reference

## 🚀 Quick Start (30 seconds)

```bash
# 1. Clone & Install
git clone https://github.com/MASSIVEMAGNETICS/project-omni-omega.git
cd project-omni-omega
pip install -r requirements.txt

# 2. Start (2 terminals)
# Terminal 1:
run_backend.bat    # or: uvicorn app.main:app --port 8000

# Terminal 2:  
run_streamlit.bat  # or: streamlit run ui/app.py --server.port 8501

# 3. Open Browser
http://localhost:8501  # UI
http://localhost:8000/docs  # API
```

## 📁 Project Structure

```
app/
├── adapters/      # 5 model backends
├── engines/       # Lab engines (diagnostics, trace, train)
├── registry/      # Model discovery
├── api/           # FastAPI routes
└── main.py        # Entry point

ui/app.py          # Streamlit UI (Chat | Lab tabs)
models/            # Model manifests (auto-discovered)
victor/            # Custom backend
lab/               # Lab artifacts
tests/             # Unit + integration tests
```

## 🔧 Adding Models

### GGUF (Recommended for CPU)
```json
// models/my-model/manifest.json
{
  "id": "my-model",
  "name": "My Model",
  "adapter": "llama_cpp",
  "files": {"weights": "model.gguf"},
  "context_length": 2048,
  "defaults": {"temperature": 0.7, "max_tokens": 256, "threads": 2}
}
```

### HuggingFace
```json
{
  "id": "hf-model",
  "adapter": "hf_transformers",
  "files": {
    "weights": "username/model-name",
    "tokenizer": "username/model-name"
  },
  "context_length": 4096,
  "defaults": {"temperature": 0.7, "max_tokens": 256}
}
```

### Remote vLLM
```json
{
  "id": "vllm",
  "adapter": "vllm_remote",
  "files": {"weights": "http://your-server:8001"},
  "context_length": 4096
}
```

## 🎯 Key Features

### Chat Tab
- Select model → Load → Chat
- Adjust temperature, top_p, max_tokens
- System prompts
- Streaming responses

### Lab Tab

**Model Manager**
- View all models
- Load/unload on demand
- Check status

**Diagnostics**
- Select modes: head_roles, capabilities, safety, etc.
- Quick mode: 90-150s
- Deep mode: comprehensive
- Get recommendations

**Trace & Target**
- Trace prompts to find important components
- Test interventions (ablation, patching)
- Identify targets for training

**Live Train**
- Add corrections to queue
- Train with Hot-LoRA, DPO, or ROME
- Auto-snapshot before training
- Rollback if needed

**Tokenizer**
- Tokenize text
- View token counts

**Artifacts**
- Create Auras (behavior overlays)
- Export SkillPacks (portable bundles)
- Manage snapshots

## 🔌 API Endpoints

### Core
```bash
POST /api/models/register        # Register model
GET  /api/models                 # List all models
POST /api/models/{id}/load       # Load model
POST /api/generate               # Generate (streaming)
POST /api/models/{id}/tokenize   # Tokenize
```

### Lab
```bash
POST /api/lab/diagnostics/run    # Run diagnostics
POST /api/lab/trace              # Causal trace
POST /api/lab/train/live         # Live training
POST /api/lab/snapshot           # Create snapshot
POST /api/lab/auras/create       # Create Aura
POST /api/lab/skillpack/export   # Export SkillPack
```

Full API docs: http://localhost:8000/docs

## ⚙️ Configuration

Edit `app/config.py` or create `.env`:

```env
# API
API_HOST=0.0.0.0
API_PORT=8000

# CPU-safe defaults
DEFAULT_THREADS=2
DEFAULT_MAX_TOKENS=256
DEFAULT_TEMPERATURE=0.7

# Training
DEFAULT_LORA_RANK=2
DEFAULT_LORA_STEPS=40
DEFAULT_LORA_LR=0.0002

# Safety
AUTO_SNAPSHOT=true
AUTO_EVAL=true
```

## 🧪 Testing

```bash
# All tests
pytest tests/ -v

# Specific tests
pytest tests/unit/test_adapters.py -v
pytest tests/integration/test_api.py -v

# With coverage
pytest tests/ --cov=app

# Validate installation
python validate_install.py
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python
python --version  # Need 3.8+

# Install deps
pip install -r requirements.txt

# Check port
netstat -ano | findstr :8000
```

### Model won't load
- Check manifest syntax (JSON validator)
- Verify file paths
- Check available RAM
- Review logs in terminal

### Slow generation
- Use Q4_0 quantization
- Reduce max_tokens
- Use smaller models
- Check CPU usage

## 📊 Performance Tips

### Low-end (i5-7200U, 16GB)
- GGUF Q4_0 models
- threads=2
- max_tokens=128-256
- Quick diagnostics
- Single model loaded

### High-end
- GGUF Q8 or FP16 models
- threads=CPU cores
- max_tokens=512-2048
- Deep diagnostics
- Multiple models OK

## 🔒 Security

- Runs entirely locally
- No external data transmission (except remote adapters)
- Victor backends sandboxed
- Auto-snapshot before changes
- Rollback capability

## 📚 Resources

- **Full Docs**: README.md
- **Setup Guide**: SETUP.md
- **Implementation**: IMPLEMENTATION_SUMMARY.md
- **API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/MASSIVEMAGNETICS/project-omni-omega

## 💡 Tips

1. **Start with Victor**: Works out of the box, no downloads
2. **Use Quick Diagnostics**: Fast overview of capabilities
3. **Snapshot Before Training**: Always create snapshot first
4. **Monitor Resources**: Keep an eye on RAM usage
5. **Use Queue**: Batch corrections for efficient training

## 🎓 Learning Path

1. **Day 1**: Set up, load Victor, try Chat
2. **Day 2**: Add GGUF model, explore Lab
3. **Day 3**: Run diagnostics, try tracing
4. **Day 4**: Add training examples, create Aura
5. **Day 5**: Export SkillPack, try remote model

## ⚡ Commands Cheatsheet

```bash
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run
run_backend.bat
run_streamlit.bat

# Test
pytest tests/ -v
python validate_install.py

# Check
curl http://localhost:8000/health
curl http://localhost:8000/api/models

# Stop
Ctrl+C in terminals
```

## 🎯 Use Cases

1. **Daily AI Chat**: Use Chat tab with your models
2. **Model Evaluation**: Run diagnostics to understand capabilities
3. **Behavior Tuning**: Use Live Train to improve responses
4. **Research**: Trace and analyze model internals
5. **Development**: Build and test custom adapters

---

**Need Help?**
- Check SETUP.md for detailed troubleshooting
- Review logs in backend terminal
- Run validate_install.py
- GitHub Issues: https://github.com/MASSIVEMAGNETICS/project-omni-omega/issues
