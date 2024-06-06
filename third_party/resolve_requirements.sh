#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

VENV_DIR="/tmp/venv-$(date +%Y%m%d-%H%M%S)"
python3 -m venv ${VENV_DIR}

source ${VENV_DIR}/bin/activate

python3 -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install -U -r requirements.txt

echo "--extra-index-url https://download.pytorch.org/whl/cpu" > requirements_lock.txt
python3 -m pip freeze -r requirements.txt >> requirements_lock.txt
deactivate
