sudo echo 'deb http://security.ubuntu.com/ubuntu xenial-security main' >> /etc/apt/sources.list
sudo echo 'deb http://cz.archive.ubuntu.com/ubuntu xenial main universe' >> /etc/apt/sources.list
sudo apt-get update 
sudo apt-get install -y curl
cd ~
git clone https://bitbucket.org/gtborg/gtsam.git
cd gtsam 
git checkout 2c0c3d195558375632fa86ed42df772fce7af42b
mkdir build
cd build
cmake -DGTSAM_INSTALL_GEOGRAPHICLIB=ON -DGTSAM_WITH_EIGEN_MKL=OFF ..
make install -j64 -l64
sudo ldconfig
