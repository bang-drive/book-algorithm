#!/usr/bin/env bash

# Install Python utils.
sudo apt install -y \
    python-is-python3 \
    python3-pip \
    python3-venv \
    wget

# Install Bazelisk.
sudo wget -O /usr/bin/bazelisk https://github.com/bazelbuild/bazelisk/releases/download/v1.19.0/bazelisk-linux-amd64
sudo chmod a+x /usr/bin/bazelisk
sudo ln -sf /usr/bin/bazelisk /usr/bin/bazel
