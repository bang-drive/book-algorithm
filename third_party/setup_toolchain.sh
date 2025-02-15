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
    sudo wget -O /usr/bin/bazelisk https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64
    sudo chmod a+x /usr/bin/bazelisk
    sudo ln -sf /usr/bin/bazelisk /usr/bin/bazel
fi

if [ -x "$(command -v nvidia-smi)" ]; then
    # Decouple CUDA version from the system default as we want to align with the latest PyTorch instead of Ubuntu.
    PREFIX="/usr/local/miniconda"
    CONDA="${PREFIX}/bin/conda"
    if [ ! -x "${CONDA}" ]; then
        wget -O conda.sh https://repo.anaconda.com/miniconda/Miniconda3-py312_24.9.2-0-Linux-x86_64.sh
        sudo bash conda.sh -b -p "${PREFIX}"
        rm -f conda.sh
    fi
    sudo "${CONDA}" install -y cudnn nccl ncurses -c conda-forge
    echo "export LD_LIBRARY_PATH=\${LD_LIBRARY_PATH}:${PREFIX}/lib" >> ~/.bashrc
else
    # No GPU available, resolve a local CPU-only lock file instead of the managed GPU version.
    bash resolve_requirements.sh
fi
