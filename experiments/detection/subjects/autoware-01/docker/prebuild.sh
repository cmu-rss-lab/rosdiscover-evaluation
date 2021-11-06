#!/bin/bash
set -eu

cd /
mkdir .autoware
cd .autoware
wget https://autoware-ai.s3.us-east-2.amazonaws.com/sample_moriyama_data.tar.gz
tar zxfv sample_moriyama_data.tar.gz

eval "$(pyenv init --path)"
eval "$(pyenv init -)"

## install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  cheetah==2.4.4 \
  defusedxml==0.6.0 \
  netifaces==0.10.7
