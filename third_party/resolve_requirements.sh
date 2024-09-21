#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

VENV_DIR="/tmp/venv-$(date +%Y%m%d-%H%M%S)"

if ! [ -x "$(command -v pip)" ]; then
    sudo apt install -y python3-pip python3-venv
fi

if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
fi
source "${VENV_DIR}/bin/activate"

CPU_ONLY=false
if [ -x "$(command -v nvidia-smi)" ]; then
    ln -sf requirements_lock_gpu.txt requirements_lock.txt
else
    CPU_ONLY=true
    ln -sf requirements_lock_cpu.txt requirements_lock.txt
fi
# The actual content change will be tracked in either cpu or gpu lock file.
git update-index --assume-unchanged requirements_lock.txt
echo -n "" > requirements_lock.txt

if [ ${CPU_ONLY} = true ]; then
    # Preinstall torch-cpu before resolving requirements.txt.
    INDEX_URL="https://download.pytorch.org/whl/cpu"
    python3 -m pip install torch torchvision --index-url "${INDEX_URL}"
    echo "--extra-index-url ${INDEX_URL}" > requirements_lock.txt
fi

python3 -m pip install -U -r requirements.txt
python3 -m pip freeze -r requirements.txt >> requirements_lock.txt

deactivate
rm -rf "${VENV_DIR}"

if [ ${CPU_ONLY} = true ]; then
    echo "
        Warning: You are in CPU-only mode, which means you have no GPU or proper GPU driver available.
                 It's not common, as this repo works better with GPU.
    "
fi
