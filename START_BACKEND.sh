#!/bin/bash

echo "========================================"
echo "FastMig Backend - Conda Environment"
echo "========================================"
echo ""

cd "$(dirname "$0")/python-backend"

echo "Activating conda environment fastmig..."

if [ -f ~/anaconda3/etc/profile.d/conda.sh ]; then
    source ~/anaconda3/etc/profile.d/conda.sh
elif [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then
    source ~/miniconda3/etc/profile.d/conda.sh
elif [ -f /opt/conda/etc/profile.d/conda.sh ]; then
    source /opt/conda/etc/profile.d/conda.sh
else
    echo "ERROR: Could not find conda installation"
    exit 1
fi

conda activate fastmig
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate conda environment"
    exit 1
fi

echo ""
echo "Starting FastMig Backend Server..."
echo "Server will be available at http://localhost:5000"
echo ""

python server.py
