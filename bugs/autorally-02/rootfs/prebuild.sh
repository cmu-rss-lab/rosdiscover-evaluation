sudo echo 'deb http://security.ubuntu.com/ubuntu xenial-security main' >> /etc/apt/sources.list
sudo echo 'deb http://cz.archive.ubuntu.com/ubuntu xenial main universe' >> /etc/apt/sources.list
sudo apt-get update 
sudo apt-get install -y curl
cd ~
git clone https://bitbucket.org/gtborg/gtsam.git
cd gtsam 
git checkout c827d4cd6b11f78f3d2d9d52b335ac562a2757fc
mkdir build
cd build
cmake -DGTSAM_INSTALL_GEOGRAPHICLIB=ON -DGTSAM_WITH_EIGEN_MKL=OFF ..
make install -j64 -l64
sudo ldconfig
