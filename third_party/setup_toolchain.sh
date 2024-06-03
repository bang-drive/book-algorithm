#!/usr/bin/env bash

# Install Python utils.
sudo apt install -y \
    flake8 \
    python-is-python3 \
    python3-pip \
    python3-venv \
    wget

# Install PyTorch, refer to https://pytorch.org/get-started/locally
# It is too big to be packed with the Bazel workspace.
if ! [ -x "$( command -v nvidia-smi )" ]; then
    python3 -m pip install torch torchvision
else
    python3 -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
fi

# Install Bazelisk.
sudo wget -O /usr/bin/bazelisk https://github.com/bazelbuild/bazelisk/releases/download/v1.20.0/bazelisk-linux-amd64
sudo chmod a+x /usr/bin/bazelisk
sudo ln -sf /usr/bin/bazelisk /usr/bin/bazel
