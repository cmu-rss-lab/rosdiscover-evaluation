#!/bin/bash
set -eu
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

## install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  cheetah==2.4.4 \
  defusedxml==0.6.0 \
  netifaces==0.10.7

# _gencpp has been replaced by _generate_messages_cpp
find /ros_ws/src -name CMakeLists.txt -print | xargs -n1 sed -i "s#_gencpp#_generate_messages_cpp#g"
