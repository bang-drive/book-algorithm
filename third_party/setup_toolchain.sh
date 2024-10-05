#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

# Install Python utils.
sudo apt install -y \
    flake8 \
    python-is-python3 \
    python3-pip \
    python3-venv \
    wget

# Install Bazelisk.
if ! [ -x "$(command -v bazelisk)" ]; then
    sudo wget -O /usr/bin/bazelisk https://github.com/bazelbuild/bazelisk/releases/download/v1.22.0/bazelisk-linux-amd64
    sudo chmod a+x /usr/bin/bazelisk
    sudo ln -sf /usr/bin/bazelisk /usr/bin/bazel
fi

# No GPU available, resolve a local CPU-only lock file instead of the managed GPU version.
if ! [ -x "$(command -v nvidia-smi)" ]; then
    bash resolve_requirements.sh
fi
