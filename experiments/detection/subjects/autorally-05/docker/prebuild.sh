#!/bin/bash
set -eu

#echo 'deb http://security.ubuntu.com/ubuntu xenial-security main' >> /etc/apt/sources.list
#echo 'deb http://cz.archive.ubuntu.com/ubuntu xenial main universe' >> /etc/apt/sources.list
#apt-get update
#apt-get install -y curl
#
echo "installing cuda"
export DEBIAN_FRONTEND=noninteractive \
&& wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/cuda-repo-ubuntu1404_6.5-14_amd64.deb \
&& dpkg -i cuda-repo-ubuntu1404_6.5-14_amd64.deb \
&& apt-get update -y \
&& apt-get install -y --no-install-recommends cuda
echo "installed cuda"

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

echo "installing geographiclib"
cd /tmp
wget -nv https://sourceforge.net/projects/geographiclib/files/distrib/GeographicLib-1.48.tar.gz
tar xfpz GeographicLib-1.48.tar.gz
cd GeographicLib-1.48
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j64
make install
echo "installed geographiclib"

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