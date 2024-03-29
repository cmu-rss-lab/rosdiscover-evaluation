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

# add a missing dependency
sed -i "11i\ diagnostic_updater" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ imu_3dm_gx4" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ visualization_msgs" /ros_ws/src/autorally/autorally_core/CMakeLists.txt
sed -i "6i\ diagnostic_updater" /ros_ws/src/autorally/autorally_control/CMakeLists.txt
sed -i "6i\ visualization_msgs" /ros_ws/src/autorally/autorally_control/CMakeLists.txt

# remove a bad dependency
sed -i "s# RingBuffer)#)#" /ros_ws/src/autorally/autorally_control/src/ConstantSpeedController/CMakeLists.txt

find /ros_ws/src -name CMakeLists.txt -print | xargs -n1 sed -i "s#_gencpp#_generate_messages_cpp#g"

echo "installing geographiclib"
cd /tmp
wget -nv --no-check-certificate https://sourceforge.net/projects/geographiclib/files/distrib/GeographicLib-1.48.tar.gz
tar xfpz GeographicLib-1.48.tar.gz
cd GeographicLib-1.48
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j64
make install
echo "installed geographiclib"

echo "installing cnpy"
git clone https://github.com/rogersce/cnpy.git /opt/cnpy
cd /opt/cnpy
git checkout cf4aab6de4338679b589cda00c24566a49213eec
cd ..
mkdir build
cd build
cmake ../cnpy
make
make install
echo "installed cnpy"

echo "installing gtsam"
git clone https://github.com/borglab/gtsam /opt/gtsam
cd /opt/gtsam
git checkout 2c0c3d195558375632fa86ed42df772fce7af42b
mkdir build
cd build
cmake -DGTSAM_INSTALL_GEOGRAPHICLIB=OFF -DGTSAM_WITH_EIGEN_MKL=OFF ..
make -j16
make install
ldconfig
echo "installed gtsam"
