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

