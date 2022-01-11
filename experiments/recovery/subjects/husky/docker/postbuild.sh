#!/bin/bash
set -eu
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

pip install pycryptodome pycryptodomex gnupg

sed -i "30i <arg name=\"initial_pose_a\" value=\"0.0\"/>" /ros_ws/src/husky/husky_navigation/launch/amcl_demo.launch
sed -i "30i <arg name=\"initial_pose_y\" value=\"0.0\"/>" /ros_ws/src/husky/husky_navigation/launch/amcl_demo.launch
sed -i "30i <arg name=\"initial_pose_x\" value=\"0.0\"/>" /ros_ws/src/husky/husky_navigation/launch/amcl_demo.launch
