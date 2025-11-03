#!/usr/bin/env python
"""
Quick validation script for OmniLoader installation
"""
import sys
from pathlib import Path

print("=" * 60)
print("OmniLoader Installation Validation")
print("=" * 60)
print()

# Check Python version
print("✓ Python version:", sys.version.split()[0])

# Check core imports
try:
    import fastapi
    print("✓ FastAPI installed:", fastapi.__version__)
except ImportError:
    print("✗ FastAPI not installed")
    sys.exit(1)

try:
    import streamlit
    print("✓ Streamlit installed:", streamlit.__version__)
except ImportError:
    print("✗ Streamlit not installed")
    sys.exit(1)

try:
    import pydantic
    print("✓ Pydantic installed:", pydantic.__version__)
except ImportError:
    print("✗ Pydantic not installed")
    sys.exit(1)

print()

# Check project structure
base_dir = Path(__file__).parent
required_dirs = [
    "app/adapters",
    "app/engines",
    "app/registry",
    "app/api",
    "ui",
    "models",
    "victor",
    "lab",
    "tests/unit",
    "tests/integration"
]

print("Checking project structure:")
for dir_path in required_dirs:
    full_path = base_dir / dir_path
    if full_path.exists():
        print(f"✓ {dir_path}")
    else:
        print(f"✗ {dir_path} missing")

print()

# Check model manifests
model_dirs = [
    "models/example_llama",
    "models/example_mistral",
    "models/example_onnx",
    "models/example_vllm"
]

print("Checking example models:")
for model_dir in model_dirs:
    manifest_path = base_dir / model_dir / "manifest.json"
    if manifest_path.exists():
        print(f"✓ {model_dir}")
    else:
        print(f"✗ {model_dir}/manifest.json missing")

print()

# Check Victor backend
victor_files = ["victor/runner.py", "victor/config.yaml", "victor/manifest.json"]
print("Checking Victor backend:")
for file_path in victor_files:
    full_path = base_dir / file_path
    if full_path.exists():
        print(f"✓ {file_path}")
    else:
        print(f"✗ {file_path} missing")

print()

# Test imports
print("Testing module imports:")
try:
    from app.registry.model_registry import ModelRegistry
    print("✓ ModelRegistry")
except ImportError as e:
    print(f"✗ ModelRegistry: {e}")

try:
    from app.adapters.llama_cpp_adapter import LlamaCppAdapter
    print("✓ LlamaCppAdapter")
except ImportError as e:
    print(f"✗ LlamaCppAdapter: {e}")

try:
    from app.engines.diagnostics import DiagnosticsEngine
    print("✓ DiagnosticsEngine")
except ImportError as e:
    print(f"✗ DiagnosticsEngine: {e}")

try:
    from app.main import app
    print("✓ FastAPI app")
except ImportError as e:
    print(f"✗ FastAPI app: {e}")

print()

# Summary
print("=" * 60)
print("Validation complete!")
print()
print("Next steps:")
print("1. Run backend: run_backend.bat (or uvicorn app.main:app)")
print("2. Run UI: run_streamlit.bat (or streamlit run ui/app.py)")
print("3. Access UI: http://localhost:8501")
print("4. Access API: http://localhost:8000/docs")
print("=" * 60)
