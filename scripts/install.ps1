# =====================================================================
# OmniLoader Studio - One-Click Install Script (Windows PowerShell)
# =====================================================================

$ErrorActionPreference = "Stop"

Write-Host "================================" -ForegroundColor Blue
Write-Host "OmniLoader Studio - Install" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

# Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Blue
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
    
    # Check Python version >= 3.8
    $version = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $majorMinor = $version.Split('.')
    $major = [int]$majorMinor[0]
    $minor = [int]$majorMinor[1]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "ERROR: Python 3.8+ is required (found $version)" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

# Check pip
try {
    $pipVersion = & python -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "pip not found"
    }
    Write-Host "✓ pip is available" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: pip is not installed" -ForegroundColor Red
    Write-Host "Please ensure pip is installed with Python" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Create virtual environment
Write-Host "[2/4] Setting up virtual environment..." -ForegroundColor Blue
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    & python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..."
& python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Blue
Write-Host "This may take 5-15 minutes depending on your connection..."
& python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Validate installation
Write-Host "[4/4] Validating installation..." -ForegroundColor Blue
if (Test-Path "validate_install.py") {
    & python validate_install.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Installation validated" -ForegroundColor Green
    }
    else {
        Write-Host "Warning: Validation had issues, but installation completed" -ForegroundColor Yellow
    }
}
else {
    Write-Host "Skipping validation (validate_install.py not found)" -ForegroundColor Yellow
}
Write-Host ""

# Success message
Write-Host "================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Run the app: .\scripts\run.ps1"
Write-Host "  2. Or use VS Code: Run Task → ⚡ Run (One Click)"
Write-Host "  3. Access UI at: http://localhost:8501"
Write-Host ""
Write-Host "Ready to run OmniLoader Studio!" -ForegroundColor Green
