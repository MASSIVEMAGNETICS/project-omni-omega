.PHONY: help setup install run dev test clean

# Default target
help:
	@echo "OmniLoader Studio - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "  make setup    - Install dependencies (one-click setup)"
	@echo "  make install  - Same as setup"
	@echo "  make run      - Start OmniLoader Studio (backend + UI)"
	@echo "  make dev      - Start in development mode (same as run)"
	@echo "  make test     - Run all tests"
	@echo "  make clean    - Remove virtual environment and caches"
	@echo ""
	@echo "Quick start:"
	@echo "  make setup && make run"
	@echo ""
	@echo "Or use VS Code:"
	@echo "  Run Task → ⚡ Install + Run (One Click)"
	@echo ""

# Install dependencies
setup install:
	@if [ "$$(uname)" = "Darwin" ] || [ "$$(uname)" = "Linux" ]; then \
		./scripts/install.sh; \
	else \
		powershell -ExecutionPolicy Bypass -File ./scripts/install.ps1; \
	fi

# Run the application
run dev:
	@if [ "$$(uname)" = "Darwin" ] || [ "$$(uname)" = "Linux" ]; then \
		./scripts/run.sh; \
	else \
		powershell -ExecutionPolicy Bypass -File ./scripts/run.ps1; \
	fi

# Run tests
test:
	@if [ -d "venv" ]; then \
		. venv/bin/activate && pytest tests/ -v; \
	else \
		echo "Error: Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Clean up
clean:
	@echo "Cleaning up..."
	@rm -rf venv
	@rm -rf __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete"
