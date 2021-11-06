#!/bin/bash
set -eu

git config --global user.email "you@example.com"
git config --global user.name "Your Name"
cd /ros_ws/src/autoware/ros
git cherry-pick f504f37fb5e4ea7152b0101e155231ab6d2a9011

eval "$(pyenv init --path)"
eval "$(pyenv init -)"

## install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  cheetah==2.4.4 \
  defusedxml==0.6.0 \
  netifaces==0.10.7
