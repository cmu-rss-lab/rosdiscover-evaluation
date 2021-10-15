#!/bin/bash
set -eu

EIGEN_VERSION="3.3.7"
GTSAM_VERSION=2c44ee459bc8090364ca8034e2988d3e8a01c422
CNPY_VERSION=4e8810b1a8637695171ed346ce68f6984e585ef4

# add a missing dependency
sed -i "11i\ diagnostic_updater" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ imu_3dm_gx4" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ visualization_msgs" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ diagnostic_updater" /ros_ws/src/autorally/autorally_control/CMakeLists.txt
sed -i "6i\ visualization_msgs" /ros_ws/src/autorally/autorally_control/CMakeLists.txt

# remove a bad dependency
sed -i "s# RingBuffer)#)#" /ros_ws/src/autorally/autorally_control/src/ConstantSpeedController/CMakeLists.txt

# _gencpp has been replaced by _generate_messages_cpp
find /ros_ws/src -name CMakeLists.txt -print | xargs -n1 sed -i "s#_gencpp#_generate_messages_cpp#g"
# sed -i "s#autorally_msgs_gencpp#autorally_msgs_generate_messages_cpp#g" /ros_ws/src/autorally/autorally_core/src/StateEstimator/CMakeLists.txt

# install cnpy
echo "installing cnpy"
git clone https://github.com/rogersce/cnpy /tmp/cnpy
cd /tmp/cnpy
git checkout "${CNPY_VERSION}"
mkdir build
cd build
cmake ..
make
make install
rm -rf /tmp/cnpy
cd /tmp
echo "installed cnpy"


# ensure that the python environment is correctly configured
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  defusedxml==0.6.0 \
  netifaces==0.10.7

# geographiclib
echo "installing geographiclib"
cd /tmp
wget -nv https://sourceforge.net/projects/geographiclib/files/distrib/GeographicLib-1.50.1.tar.gz
tar xfpz GeographicLib-1.50.1.tar.gz
cd GeographicLib-1.50.1
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j8
make install
rm -rf /tmp/GeographicLib*
echo "installed geographiclib"

# gtsam
echo "installing gtsam"
cd /tmp
git clone https://github.com/borglab/gtsam /tmp/gtsam
cd /tmp/gtsam
git checkout "${GTSAM_VERSION}"
mkdir build
cd build
cmake -DGTSAM_INSTALL_GEOGRAPHICLIB=OFF -DGTSAM_WITH_EIGEN_MKL=OFF ..
make -j8
make install
ldconfig
rm -rf /tmp/gtsam
echo "installed gtsam"

# flycapture
echo "installing flycapture"
cd /tmp
mkdir /tmp/flycapture
tar -C /tmp/flycapture -xvf /.dockerinstall/flycapture2-2.13.3.31-amd64-pkg_Ubuntu18.04.tgz
cd /tmp/flycapture/flycapture*
dpkg -i libflycapture-2*
dpkg -i libflycapturegui-2*
dpkg -i libflycapturevideo-2*
dpkg -i libflycapture-c-2*
dpkg -i libflycapturegui-c-2*
dpkg -i libflycapturevideo-c-2*
dpkg -i libmultisync-2*
dpkg -i libmultisync-c-2*
dpkg -i flycap-2*
dpkg -i flycapture-doc-2*
dpkg -i updatorgui*
rm -rf /tmp/flycapture
echo "installed flycapture"

# eigen
cd /tmp
echo "building eigen [version: ${EIGEN_VERSION}]"
git clone https://github.com/eigenteam/eigen-git-mirror /tmp/eigen
cd /tmp/eigen
git checkout "${EIGEN_VERSION}"
mkdir build
cd build
cmake ..
make -j8
make install
rm -rf /tmp/eigen
echo "built eigen ${EIGEN_VERSION}"

# SEE: https://github.com/AutoRally/autorally/issues/88
# cp /.dockerinstall/StateEstimator_CMakeLists.fixed.txt /ros_ws/src/autorally/autorally_core/src/StateEstimator/CMakeLists.txt

#echo "fixing shared library locations (see: https://github.com/AutoRally/autorally/issues/84)"
#ln -s /usr/local/lib/libgtsam.so.4.0.2 /usr/local/lib/libgtsam.so
#echo "fixed shared library locations"
