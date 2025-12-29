#!/bin/bash

echo "========================================"
echo "FastMig Environment Setup"
echo "========================================"
echo ""

if [ -f ~/anaconda3/etc/profile.d/conda.sh ]; then
    source ~/anaconda3/etc/profile.d/conda.sh
elif [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then
    source ~/miniconda3/etc/profile.d/conda.sh
elif [ -f /opt/conda/etc/profile.d/conda.sh ]; then
    source /opt/conda/etc/profile.d/conda.sh
else
    echo "ERROR: Could not find conda"
    exit 1
fi

echo "Creating fastmig environment..."
conda create -n fastmig python=3.10 -y

echo ""
echo "Installing packages..."
conda activate fastmig
pip install -r "$(dirname "$0")/python-backend/requirements.txt"

echo ""
echo "Setup complete!"
