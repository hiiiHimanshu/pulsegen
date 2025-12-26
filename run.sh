#!/bin/bash
# Helper script to run the project with proper environment setup

# Set HuggingFace cache directory
export HF_HOME=$(pwd)/.cache/huggingface
export TRANSFORMERS_CACHE=$(pwd)/.cache/huggingface

# Create cache directory if it doesn't exist
mkdir -p .cache/huggingface

# Activate virtual environment
source venv/bin/activate

# Run the main script with all arguments
python3 main.py "$@"

