#!/bin/bash
set -eu
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
# eval "$(pyenv virtualenv-init -)"

## install necessary python packages
#pip install \
#  sip==4.19.18

# see
# - https://github.com/ros/geometry/issues/144
# - https://github.com/ros/ros_comm/pull/962
sed -i "s#^  INCLUDE_DIRS include\$#  INCLUDE_DIRS include include/xmlrpcpp#" /ros_ws/src/ros_comm/xmlrpcpp/CMakeLists.txt

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

#cd /tmp
#wget https://www.riverbankcomputing.com/static/Downloads/sip/4.19.25/sip-4.19.25.tar.gz
#tar zxf sip-4.19.25.tar.gz
#cd sip-4.19.25
#python configure.py
#make install
#rm -rf /tmp/*

#cd /tmp
#wget https://files.pythonhosted.org/packages/19/5a/c50a0ccd211f864972da0f2e101722508ffb4e008347fd2a56a99beab9d0/sip-4.19.2-cp35-cp35m-manylinux1_x86_64.whl
#pip install sip-4.19.2-cp35-cp35m-manylinux1_x86_64.whl
