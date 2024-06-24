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

# install opencv3.2.0
echo "installing opencv"
sudo apt-get -y update 
sudo apt-get -y upgrade
sudo apt-get install -y build-essential
sudo apt-get install -y cmake
sudo apt-get install -y qt5-default libvtk6-dev
sudo apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libjasper-dev libopenexr-dev libgdal-dev
sudo apt-get install -y libtbb-dev libeigen3-dev
sudo apt-get install -y python-dev python-tk python-numpy python3-dev python3-tk python3-numpy
sudo apt-get install -y ant default-jdk
sudo apt-get install -y doxygen
sudo apt-get install -y unzip wget
wget https://github.com/opencv/opencv/archive/3.2.0.zip -O OpenCV320.zip
unzip OpenCV320.zip
cd OpenCV320
mkdir build
cd build
cmake -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON ..
make -j4
sudo make install
sudo ldconfig