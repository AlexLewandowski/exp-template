#!/usr/bin/env sh

config=$1
# total_gpus=$(nvidia-smi -L | wc -l)
# gpu=$((${2:-0} % total_gpus))  # Subtract 1 from the input, default to 0 if not provided

if command -v nvidia-smi &> /dev/null; then
    total_gpus=$(nvidia-smi -L | wc -l)
    gpu=$((${2:-0} % total_gpus))  # Subtract 1 from the input, default to 0 if not provided
    XLA_PYTHON_CLIENT_PREALLOCATE=false CUDA_VISIBLE_DEVICES=$gpu python -m src.train "$1"
else
    echo "nvidia-smi not found, skipping GPU configuration"
    python -m src.train "$1"
fi
