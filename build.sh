#!/bin/bash
# Build script for deployment

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Set environment variables to avoid compilation
export PANDAS_SKIP_BUILD=1
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Install pandas with pre-compiled binaries only
pip install --no-cache-dir --only-binary=all pandas==1.5.3

# Install other dependencies
pip install --no-cache-dir -r requirements.txt

# Make the script executable
chmod +x build.sh 