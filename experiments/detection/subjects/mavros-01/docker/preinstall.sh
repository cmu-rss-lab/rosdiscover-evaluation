#!/bin/bash
set -eu
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | python2.7
