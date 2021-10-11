#!/bin/bash
set -eu

# ensure that the python environment is correctly configured
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6
