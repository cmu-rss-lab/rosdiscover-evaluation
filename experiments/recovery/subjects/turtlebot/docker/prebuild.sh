#!/bin/bash
set -eu
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

## install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  defusedxml==0.7.1 \
  netifaces==0.11.0

# see
# - https://github.com/ros/geometry/issues/144
# - https://github.com/ros/ros_comm/pull/962
sed -i "s#^  INCLUDE_DIRS include\$#  INCLUDE_DIRS include include/xmlrpcpp#" /ros_ws/src/ros_comm/xmlrpcpp/CMakeLists.txt

# see
# - https://github.com/wg-perception/people/issues/96
# - https://github.com/wg-perception/people/pull/97/files
sed -i "s#\${BFL_INCLUDE_DIRS}#\${BFL_INCLUDE_DIRS}/..#" /ros_ws/src/navigation/robot_pose_ekf/CMakeLists.txt

# fix another broken CMakeLists.txt
sed -i "4inav_msgs" src/kobuki/kobuki_auto_docking/CMakeLists.txt

# see: https://answers.ros.org/question/313893/unabe-to-install-freenect-in-ros-melodicubuntu-1804/
git clone https://github.com/OpenKinect/libfreenect.git /tmp/libfreenect
cd /tmp/libfreenect
git checkout v0.5.5
mkdir build
cd build
cmake ..
make
make install
rm -rf /tmp/*
