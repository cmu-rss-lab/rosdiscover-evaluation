#!/bin/bash
set -e

EIGEN_VERSION="3.3.7"

echo "installing geographiclib"
cd /tmp
wget -nv https://sourceforge.net/projects/geographiclib/files/distrib/GeographicLib-1.50.1.tar.gz
tar xfpz GeographicLib-1.50.1.tar.gz
cd GeographicLib-1.50.1
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j64
make install
echo "installed geographiclib"

echo "installing gtsam"
git clone https://github.com/borglab/gtsam /opt/gtsam
cd /opt/gtsam
git checkout 2c44ee459bc8090364ca8034e2988d3e8a01c422
mkdir build
cd build
cmake -DGTSAM_INSTALL_GEOGRAPHICLIB=OFF -DGTSAM_WITH_EIGEN_MKL=OFF ..
make -j64
make install
ldconfig
echo "installed gtsam"

echo "installing flycapture"
mkdir /opt/flycapture
cd /opt/flycapture
tar -xvf /.dockerinstall/flycapture2-2.13.3.31-amd64-pkg_Ubuntu18.04.tgz
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

echo "building eigen ${EIGEN_VERSION}"
git clone https://github.com/eigenteam/eigen-git-mirror /opt/eigen
cd /opt/eigen
git checkout "${EIGEN_VERSION}"
mkdir build
cd build
cmake ..
make install
echo "built eigen ${EIGEN_VERSION}"

wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.44-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1604_8.0.44-1_amd64.deb
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends cuda

cd ~
git clone https://github.com/rogersce/cnpy.git
mkdir build
cd build 
cmake ../cnpy
make
make install
