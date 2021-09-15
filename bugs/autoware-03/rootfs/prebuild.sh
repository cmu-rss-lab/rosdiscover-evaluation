curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | python2.7

wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/cuda-repo-ubuntu1404_6.5-14_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1404_6.5-14_amd64.deb
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends cuda
