#!/bin/bash
set -eu

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
GEOGRAPHICLIB_VERSION="1.48"
CNPY_VERSION=be30d504dd810f4a444b1c4ac08db58dc6fbd39c
GTSAM_VERSION=2c44ee459bc8090364ca8034e2988d3e8a01c422

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
cd /tmp
rm -rf /tmp/gtsam
echo "installed gtsam"

# cnpy
echo "installing cnpy"
cd /tmp
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

# flycapture
echo "installing flycapture"
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

# eigen
echo "building eigen ${EIGEN_VERSION}"
git clone https://github.com/eigenteam/eigen-git-mirror /opt/eigen
cd /opt/eigen
git checkout "${EIGEN_VERSION}"
mkdir build
cd build
cmake ..
make install
echo "built eigen ${EIGEN_VERSION}"

# WARNING: this is bad!
apt-get update
apt-get install -y libgtkmm-2.4-1v5
apt --fix-broken install -y
