#!/bin/bash
set -eu

sed -i 's/\.\//\/ros_ws\/src\/autoware\/ros\//' /ros_ws/src/autoware/ros/src/util/packages/model_publisher/launch/vehicle_model.launch

eval "$(pyenv init --path)"
eval "$(pyenv init -)"

## install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  cheetah==2.4.4 \
  defusedxml==0.6.0 \
  netifaces==0.10.7
