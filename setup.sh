#!/bin/bash -e
set -euo pipefail
IFS=$'\n\t'


mkdir -p Venv
python3 -m venv Venv

source Venv/bin/activate

pip install numpy scipy matplotlib

python3 test.py

deactivate
