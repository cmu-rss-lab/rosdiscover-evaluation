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
  netifaces==0.10.7 \
  future

# geographiclib
GEOGRAPHICLIB_VERSION="1.48"
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

sh /ros_ws/src/mavros/mavros/scripts/install_geographiclib_datasets.sh
