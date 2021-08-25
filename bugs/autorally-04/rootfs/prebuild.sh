wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/cuda-repo-ubuntu1404_6.5-14_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1404_6.5-14_amd64.deb
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends cuda

sudo echo 'deb http://security.ubuntu.com/ubuntu xenial-security main' >> /etc/apt/sources.list
sudo echo 'deb http://cz.archive.ubuntu.com/ubuntu xenial main universe' >> /etc/apt/sources.list
sudo apt-get update 
sudo apt-get install -y curl

git clone https://github.com/rogersce/cnpy.git
cd cnpy 
git checkout cf4aab6de4338679b589cda00c24566a49213eec
cd ..
mkdir build
cd build 
cmake ../cnpy
make
make install

cd ~
git clone https://bitbucket.org/gtborg/gtsam.git
cd gtsam 
git checkout 2c0c3d195558375632fa86ed42df772fce7af42b
mkdir build
cd build
cmake -DGTSAM_INSTALL_GEOGRAPHICLIB=ON -DGTSAM_WITH_EIGEN_MKL=OFF ..
make install -j64 -l64
sudo ldconfig
cd /pre_bug/src 
git clone https://github.com/AutoRally/imu_3dm_gx4.git
cp -r imu_3dm_gx4 /bug/src/
cp -r imu_3dm_gx4 /bug_fix/src/
