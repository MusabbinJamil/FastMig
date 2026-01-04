#!/bin/bash

echo "========================================"
echo "FastMig Backend Server"
echo "========================================"
echo ""

cd "$(dirname "$0")/python-backend"

echo "Activating Python environment..."

# Try venv first, then conda
if [ -f ./venv/bin/activate ]; then
    echo "Using venv..."
    source ./venv/bin/activate
elif [ -f ~/anaconda3/etc/profile.d/conda.sh ]; then
    source ~/anaconda3/etc/profile.d/conda.sh
    conda activate fastmig
elif [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate fastmig
elif [ -f /opt/conda/etc/profile.d/conda.sh ]; then
    source /opt/conda/etc/profile.d/conda.sh
    conda activate fastmig
else
    echo "ERROR: Could not find Python environment (venv or conda)"
    exit 1
fi

echo ""
echo "Starting FastMig Backend Server..."
echo "Server will be available at http://localhost:5000"
echo ""

python server.py
