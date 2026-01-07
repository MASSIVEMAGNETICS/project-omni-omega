# =====================================================================
# OmniLoader Studio - One-Click Run Script (Windows PowerShell)
# =====================================================================

$ErrorActionPreference = "Stop"

# Configuration
$BACKEND_PORT = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { 8000 }
$FRONTEND_PORT = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { 8501 }

Write-Host "================================" -ForegroundColor Blue
Write-Host "OmniLoader Studio - Run" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run the install script first:" -ForegroundColor Yellow
    Write-Host "  .\scripts\install.ps1"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
try {
    & python -c "import fastapi, streamlit" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Dependencies not installed"
    }
    Write-Host "✓ Dependencies OK" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Dependencies not installed" -ForegroundColor Red
    Write-Host "Please run the install script first:" -ForegroundColor Yellow
    Write-Host "  .\scripts\install.ps1"
    exit 1
}
Write-Host ""

# Check if ports are available
Write-Host "Checking ports..." -ForegroundColor Cyan
$backendInUse = Get-NetTCPConnection -LocalPort $BACKEND_PORT -ErrorAction SilentlyContinue
$frontendInUse = Get-NetTCPConnection -LocalPort $FRONTEND_PORT -ErrorAction SilentlyContinue

if ($backendInUse) {
    Write-Host "Warning: Port $BACKEND_PORT is already in use" -ForegroundColor Yellow
    Write-Host "Backend may already be running or another service is using the port."
}

if ($frontendInUse) {
    Write-Host "Warning: Port $FRONTEND_PORT is already in use" -ForegroundColor Yellow
    Write-Host "Frontend may already be running or another service is using the port."
}
Write-Host ""

# Cleanup function
function Cleanup {
    Write-Host ""
    Write-Host "Shutting down OmniLoader Studio..." -ForegroundColor Yellow
    
    # Kill backend and frontend
    if ($script:BackendProcess) {
        Stop-Process -Id $script:BackendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($script:FrontendProcess) {
        Stop-Process -Id $script:FrontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    # Also kill by port as backup
    Get-NetTCPConnection -LocalPort $BACKEND_PORT -ErrorAction SilentlyContinue | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Get-NetTCPConnection -LocalPort $FRONTEND_PORT -ErrorAction SilentlyContinue | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "Shutdown complete" -ForegroundColor Green
}

# Register cleanup on Ctrl+C
$null = Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

# Start services
Write-Host "================================" -ForegroundColor Blue
Write-Host "Starting OmniLoader Studio..." -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""
Write-Host "Backend API:  http://localhost:$BACKEND_PORT" -ForegroundColor Green
Write-Host "API Docs:     http://localhost:$BACKEND_PORT/docs" -ForegroundColor Green
Write-Host "Studio UI:    http://localhost:$FRONTEND_PORT" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start backend
Write-Host "Starting backend..." -ForegroundColor Cyan
$script:BackendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $BACKEND_PORT -NoNewWindow -PassThru
Write-Host "✓ Backend started (PID: $($script:BackendProcess.Id))" -ForegroundColor Green

# Wait for backend to be ready
Write-Host "Waiting for backend..." -ForegroundColor Cyan
$ready = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$BACKEND_PORT/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Backend is ready" -ForegroundColor Green
            $ready = $true
            break
        }
    }
    catch {
        # Continue waiting
    }
    Start-Sleep -Seconds 1
}

if (-not $ready) {
    Write-Host "ERROR: Backend failed to start" -ForegroundColor Red
    Cleanup
    exit 1
}
Write-Host ""

# Start frontend
Write-Host "Starting Studio UI..." -ForegroundColor Cyan
$script:FrontendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "streamlit", "run", "ui/app.py", "--server.port", $FRONTEND_PORT, "--server.address", "0.0.0.0", "--server.headless", "true" -NoNewWindow -PassThru
Write-Host "✓ Studio UI started (PID: $($script:FrontendProcess.Id))" -ForegroundColor Green
Write-Host ""

# Wait a moment for frontend to start
Start-Sleep -Seconds 3

# Open browser
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:$FRONTEND_PORT"
Write-Host ""

Write-Host "================================" -ForegroundColor Green
Write-Host "OmniLoader Studio is running!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access at:"
Write-Host "  • Studio UI: http://localhost:$FRONTEND_PORT"
Write-Host "  • API Docs:  http://localhost:$BACKEND_PORT/docs"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Check if processes are still running
        if (-not (Get-Process -Id $script:BackendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "Backend process terminated unexpectedly" -ForegroundColor Red
            break
        }
        if (-not (Get-Process -Id $script:FrontendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "Frontend process terminated unexpectedly" -ForegroundColor Red
            break
        }
    }
}
finally {
    Cleanup
}
