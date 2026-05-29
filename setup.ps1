# Nalam Project Setup Script (PowerShell)
# Run this once to set up the entire project locally

$ErrorActionPreference = "Stop"

Write-Output "=========================================="
Write-Output "Nalam Project Setup"
Write-Output "=========================================="
Write-Output ""

# Check Python version
Write-Output "[1/5] Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Output "  Python version: $pythonVersion"
} catch {
    Write-Error "Python 3 not found. Please install Python 3.11+"
    exit 1
}
Write-Output ""

# Backend setup
Write-Output "[2/5] Setting up backend..."
Push-Location nalam
pip install -r requirements.txt
Write-Output "  Backend dependencies installed"
Pop-Location
Write-Output ""

# Knowledge base setup
Write-Output "[3/5] Building knowledge base vector store..."
Push-Location knowledge_base

# Check for API key
$apiKey = $env:GOOGLE_API_KEY
if (-not $apiKey) {
    if (Test-Path ".env") {
        Get-Content ".env" | ForEach-Object {
            if ($_ -match '^\s*([^=]+)=(.*)$') {
                [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
            }
        }
        $apiKey = $env:GOOGLE_API_KEY
        Write-Output "  Loaded API key from .env"
    } else {
        Write-Error "GOOGLE_API_KEY not found."
        Write-Output "Set it with: `$env:GOOGLE_API_KEY = 'your-key'"
        Write-Output "Or create knowledge_base/.env with: GOOGLE_API_KEY=your-key"
        exit 1
    }
}

pip install -r requirements.txt
Write-Output "  Knowledge base dependencies installed"

# Build FAISS index
Write-Output "  Building FAISS vector store (this takes a few minutes)..."
python build-index.py

if (-not (Test-Path "embeddings/faiss_index.bin")) {
    Write-Error "Vector store build failed"
    exit 1
}
Write-Output "  Vector store built successfully"
Pop-Location
Write-Output ""

# Frontend setup
Write-Output "[4/5] Setting up frontend..."
Push-Location nalam
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Output "  Created .env from .env.example"
}
npm install
npm run build
Write-Output "  Frontend built successfully"
Pop-Location
Write-Output ""

# Verification
Write-Output "[5/5] Verifying setup..."
python verify-production-ready.py

if ($LASTEXITCODE -eq 0) {
    Write-Output ""
    Write-Output "=========================================="
    Write-Output "SETUP COMPLETE - Ready for local development!"
    Write-Output "=========================================="
    Write-Output ""
    Write-Output "Start development servers:"
    Write-Output "  PowerShell: `$env:FLASK_ENV = 'development'; cd nalam; python backend.py"
    Write-Output "  (Backend: http://localhost:5000)"
    Write-Output ""
    Write-Output "  PowerShell: cd nalam; npm run dev"
    Write-Output "  (Frontend: http://localhost:5173)"
    Write-Output ""
} else {
    Write-Error "Setup verification failed. Check errors above."
    exit 1
}
