#!/bin/bash
set -eu

# see
# - https://github.com/ros/geometry/issues/144
# - https://github.com/ros/ros_comm/pull/962
sed -i "s#^  INCLUDE_DIRS include\$#  INCLUDE_DIRS include include/xmlrpcpp#" /ros_ws/src/ros_comm/xmlrpcpp/CMakeLists.txt
