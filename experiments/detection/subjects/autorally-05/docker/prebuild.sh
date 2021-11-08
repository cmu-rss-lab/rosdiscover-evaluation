#!/bin/bash
set -eu

GTSAM_VERSION=2c0c3d195558375632fa86ed42df772fce7af42b
CNPY_VERSION=cf4aab6de4338679b589cda00c24566a49213eec
GEOGRAPHICLIB_VERSION="1.48"

# add a missing dependency
sed -i "11i\ diagnostic_updater" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ imu_3dm_gx4" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ visualization_msgs" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ diagnostic_updater" /ros_ws/src/autorally/autorally_control/CMakeLists.txt
sed -i "6i\ visualization_msgs" /ros_ws/src/autorally/autorally_control/CMakeLists.txt

# remove a bad dependency
sed -i "s# RingBuffer)#)#" /ros_ws/src/autorally/autorally_control/src/ConstantSpeedController/CMakeLists.txt

# ensure that the python environment is correctly configured
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  defusedxml==0.6.0 \
  netifaces==0.10.7

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

# geographiclib
echo "installing geographiclib"
cd /tmp
wget --no-check-certificate -nv "https://sourceforge.net/projects/geographiclib/files/distrib/GeographicLib-${GEOGRAPHICLIB_VERSION}.tar.gz"
tar xfpz "GeographicLib-${GEOGRAPHICLIB_VERSION}.tar.gz"
cd "GeographicLib-${GEOGRAPHICLIB_VERSION}"
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
