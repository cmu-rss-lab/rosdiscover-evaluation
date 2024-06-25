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

sed -i 's/opencv-3.2.0-dev//' /ros_ws/src/autoware/ros/src/computing/perception/detection/packages/lidar_tracker/CMakeLists.txt
