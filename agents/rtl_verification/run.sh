#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "======================================"
echo " RTL Verification API"
echo "======================================"

cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "[1/4] Activating Python virtual environment..."
    source venv/bin/activate
else
    echo "[WARNING] venv not found"
fi

# Check Python
echo "[2/4] Checking Python..."
python3 --version

# Check required tools
echo "[3/4] Checking RTL tools..."

if ! command -v make >/dev/null 2>&1; then
    echo "ERROR: make is not installed"
    exit 1
fi

if ! command -v iverilog >/dev/null 2>&1; then
    echo "ERROR: iverilog is not installed"
    exit 1
fi

if ! command -v cocotb-config >/dev/null 2>&1; then
    echo "ERROR: cocotb is not installed"
    exit 1
fi

echo "make        : OK"
echo "iverilog    : OK"
echo "cocotb      : OK"

# Create result directories
mkdir -p results/logs
mkdir -p results/waveforms

echo "[4/4] Starting FastAPI..."

echo ""
echo "======================================"
echo " API running at:"
echo " http://127.0.0.1:8000"
echo ""
echo " Swagger UI:"
echo " http://127.0.0.1:8000/docs"
echo "======================================"
echo ""

exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
