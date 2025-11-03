# OmniLoader Setup Guide

## Complete Installation Instructions

### 1. System Requirements

**Minimum:**
- Windows 10 Home
- Intel i5-7200U (2C/4T) or equivalent
- 16 GB RAM
- 10 GB free disk space
- Python 3.8+

**Recommended:**
- Windows 10/11 Pro
- Intel i7 or AMD Ryzen 5+ (4C/8T)
- 32 GB RAM
- 50 GB free disk space (for models)
- Python 3.10+

### 2. Python Installation

1. Download Python from https://www.python.org/downloads/
2. During installation:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"
3. Verify installation:
   ```bash
   python --version
   pip --version
   ```

### 3. Clone Repository

```bash
git clone https://github.com/MASSIVEMAGNETICS/project-omni-omega.git
cd project-omni-omega
```

### 4. Create Virtual Environment

```bash
python -m venv venv
```

### 5. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 6. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** This may take 5-15 minutes depending on your internet connection.

### 7. Verify Installation

```bash
python -c "import fastapi, streamlit, torch; print('All dependencies installed!')"
```

## Running OmniLoader

### Option 1: Using Batch Scripts (Windows)

**Terminal 1 - Backend:**
```bash
run_backend.bat
```

**Terminal 2 - UI:**
```bash
run_streamlit.bat
```

### Option 2: Manual Commands

**Terminal 1 - Backend:**
```bash
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - UI:**
```bash
venv\Scripts\activate
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
```

### Accessing the Application

- **UI:** http://localhost:8501
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Adding Your First Model

### Option A: Using a GGUF Model (Recommended for CPU)

1. Download a GGUF model (e.g., from HuggingFace)
2. Create directory: `models/my-model/`
3. Place GGUF file in directory
4. Create `models/my-model/manifest.json`:

```json
{
  "id": "my-llama-7b",
  "name": "My LLaMA 7B",
  "adapter": "llama_cpp",
  "files": {
    "weights": "model-q4_0.gguf"
  },
  "context_length": 2048,
  "defaults": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 256,
    "threads": 2
  }
}
```

5. Restart the backend
6. Model will appear in UI sidebar

### Option B: Using HuggingFace Model

Create `models/my-hf-model/manifest.json`:

```json
{
  "id": "mistral-7b",
  "name": "Mistral 7B",
  "adapter": "hf_transformers",
  "files": {
    "weights": "mistralai/Mistral-7B-v0.1",
    "tokenizer": "mistralai/Mistral-7B-v0.1"
  },
  "context_length": 4096,
  "defaults": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 256,
    "threads": 2
  }
}
```

**Note:** Model will download from HuggingFace Hub on first load.

### Option C: Using Remote vLLM

Create `models/my-vllm/manifest.json`:

```json
{
  "id": "vllm-server",
  "name": "vLLM Server",
  "adapter": "vllm_remote",
  "files": {
    "weights": "http://your-vllm-server:8001"
  },
  "context_length": 4096,
  "defaults": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 256
  }
}
```

## Troubleshooting

### Issue: "Python not found"
**Solution:** Ensure Python is in PATH. Reinstall Python with "Add to PATH" checked.

### Issue: "Module not found" errors
**Solution:** 
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Backend won't start
**Solution:** Check if port 8000 is in use:
```bash
netstat -ano | findstr :8000
```
Kill process or change port in `app/config.py`.

### Issue: UI shows "Backend not running"
**Solution:** 
1. Ensure backend is started first
2. Check http://localhost:8000/health in browser
3. Check backend terminal for errors

### Issue: Model fails to load
**Solution:**
1. Check manifest syntax (use JSON validator)
2. Verify file paths
3. Check available RAM
4. Review backend logs

### Issue: Generation is very slow
**Solution:**
1. Use smaller/quantized models (Q4_0)
2. Reduce `max_tokens`
3. Close other applications
4. Check CPU usage

### Issue: Out of memory
**Solution:**
1. Use more aggressive quantization (Q3, Q4)
2. Reduce context_length
3. Close other applications
4. Upgrade RAM if possible

## Performance Optimization

### For CPU-Only Systems

**Use these settings in manifest:**
```json
{
  "defaults": {
    "threads": 2,
    "max_tokens": 128,
    "temperature": 0.7
  },
  "context_length": 2048
}
```

**Recommended models:**
- TinyLlama-1.1B (Q4_0)
- Phi-2 (Q4_0)
- Mistral-7B (Q3 or Q4_0)

### For GPU Systems

1. Install GPU-enabled PyTorch:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

2. For llama.cpp with GPU:
```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

3. Update manifests to use GPU:
```json
{
  "defaults": {
    "n_gpu_layers": 32
  }
}
```

## Testing Your Installation

### Run Tests

```bash
# All tests
pytest tests/ -v

# Quick smoke test
pytest tests/unit/test_adapters.py -v

# Integration tests
pytest tests/integration/ -v
```

### Manual Test

1. Start backend and UI
2. Load the Victor example model (should work out of the box)
3. Go to Chat tab
4. Send a test message
5. Verify you get a response

## Next Steps

1. **Explore Chat Tab**
   - Try different models
   - Adjust generation parameters
   - Test system prompts

2. **Explore Lab Tab**
   - Run diagnostics on a model
   - Try tokenization
   - Create a snapshot

3. **Add Your Own Models**
   - Follow examples in `models/` directory
   - Experiment with different adapters

4. **Read Full Documentation**
   - See README.md for complete feature list
   - Check API docs at http://localhost:8000/docs

## Getting Help

- GitHub Issues: https://github.com/MASSIVEMAGNETICS/project-omni-omega/issues
- Check logs in backend terminal
- Review error messages in UI

## Common Model Sources

- **GGUF Models:** https://huggingface.co/models?search=gguf
- **HuggingFace Models:** https://huggingface.co/models
- **Quantized Models:** https://huggingface.co/TheBloke

## Security Notes

- OmniLoader runs entirely locally by default
- No data is sent to external servers unless using remote adapters
- Victor custom backends are sandboxed
- Always review manifests before loading models
