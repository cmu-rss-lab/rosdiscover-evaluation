#!/bin/bash
set -e

# ensure that the python environment is correctly configured
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  defusedxml==0.6.0 \
  netifaces==0.10.7

EIGEN_VERSION="3.3.7"

echo "installing flycapture"
apt-get update
apt-get install -y libgtkmm-2.4-1v5
apt --fix-broken install -y
mkdir /opt/flycapture
cd /opt/flycapture
tar -xvf /.dockerinstall/flycapture2-2.13.3.31-amd64-pkg_Ubuntu16.04.tgz
cd flycapture*
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
echo "installed flycapture"

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
echo "installed geographiclib"

echo "installing gtsam"
git clone https://github.com/borglab/gtsam /opt/gtsam
cd /opt/gtsam
git checkout 2c44ee459bc8090364ca8034e2988d3e8a01c422
mkdir build
cd build
cmake -DGTSAM_INSTALL_GEOGRAPHICLIB=OFF -DGTSAM_WITH_EIGEN_MKL=OFF ..
make -j8
make install
ldconfig
echo "installed gtsam"

echo "installing cnpy"
git clone https://github.com/rogersce/cnpy.git /opt/cnpy
cd /opt/cnpy
git checkout 4e8810b1a8637695171ed346ce68f6984e585ef4
cd ..
mkdir build
cd build
cmake ../cnpy
make
make install
echo "installed cnpy"

echo "building eigen ${EIGEN_VERSION}"
git clone https://github.com/eigenteam/eigen-git-mirror /opt/eigen
cd /opt/eigen
git checkout "${EIGEN_VERSION}"
mkdir build
cd build
cmake ..
make install
echo "built eigen ${EIGEN_VERSION}"

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
