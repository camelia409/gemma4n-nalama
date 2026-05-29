#!/bin/bash
# Nalam Project Setup Script
# Run this once to set up the entire project locally

set -e  # Exit on error

echo "=========================================="
echo "Nalam Project Setup"
echo "=========================================="
echo

# Check Python version
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.11+."
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"
echo

# Backend setup
echo "[2/5] Setting up backend..."
cd nalam
pip install -r requirements.txt
echo "  Backend dependencies installed"
cd ..
echo

# Knowledge base setup
echo "[3/5] Building knowledge base vector store..."
cd knowledge_base

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    if [ -f ".env" ]; then
        export $(cat .env | xargs)
        echo "  Loaded API key from .env"
    else
        echo "ERROR: GOOGLE_API_KEY not found."
        echo "Set it with: export GOOGLE_API_KEY='your-key'"
        echo "Or create knowledge_base/.env with: GOOGLE_API_KEY=your-key"
        exit 1
    fi
fi

pip install -r requirements.txt
echo "  Knowledge base dependencies installed"

# Build FAISS index
echo "  Building FAISS vector store (this takes a few minutes)..."
python build-index.py

if [ ! -f "embeddings/faiss_index.bin" ]; then
    echo "ERROR: Vector store build failed"
    exit 1
fi
echo "  Vector store built successfully"
cd ..
echo

# Frontend setup
echo "[4/5] Setting up frontend..."
cd nalam
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  Created .env from .env.example"
fi
npm install
npm run build
echo "  Frontend built successfully"
cd ..
echo

# Verification
echo "[5/5] Verifying setup..."
python verify-production-ready.py

if [ $? -eq 0 ]; then
    echo
    echo "=========================================="
    echo "SETUP COMPLETE - Ready for local development!"
    echo "=========================================="
    echo
    echo "Start development servers:"
    echo "  cd nalam && FLASK_ENV=development python backend.py  # Backend: http://localhost:5000"
    echo "  cd nalam && npm run dev                               # Frontend: http://localhost:5173"
    echo
else
    echo "Setup verification failed. Check errors above."
    exit 1
fi
