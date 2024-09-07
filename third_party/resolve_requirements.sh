#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

VENV_DIR="/tmp/venv-$(date +%Y%m%d-%H%M%S)"

dpkg -l python3-venv > /dev/null 2>&1
if [ $? -ne 0 ]; then
    sudo apt install -y python3-venv
fi

if [ ! -d ${VENV_DIR} ]; then
    python3 -m venv ${VENV_DIR}
fi
source ${VENV_DIR}/bin/activate

CPU_ONLY=false
if ! [ -x "$(command -v nvidia-smi)" ]; then
    CPU_ONLY=true
    INDEX_URL="https://download.pytorch.org/whl/cpu"
    python3 -m pip install torch torchvision --index-url "${INDEX_URL}"
    echo "--extra-index-url ${INDEX_URL}" > requirements_lock.txt
else
    echo -n "" > requirements_lock.txt
fi

python3 -m pip install -U -r requirements.txt
python3 -m pip freeze -r requirements.txt >> requirements_lock.txt
deactivate

if [ ${CPU_ONLY} = true ]; then
    echo "
        Warning: You are in CPU-only mode, which means you have no GPU or proper GPU driver available.
                 It's not common, so we mark the requirements_lock.txt as unchanged in Git perspective.
                 You can continue to work on this machine with the CPU-only requirements_lock.txt, but
                 if you do want to check it in, please run the following command:
                     git update-index --no-assume-unchanged $(realpath requirements_lock.txt)

                 You should also run it before pulling an updated requirements_lock.txt from the remote repository.
    "
    git update-index --assume-unchanged requirements_lock.txt
fi
