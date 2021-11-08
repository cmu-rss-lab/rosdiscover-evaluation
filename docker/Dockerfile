# source: https://raw.githubusercontent.com/TheRobotCooperative/TheRobotCooperative/master/ros1/Dockerfile
#
# This is a generic Dockerfile that is used to build all of the images within
# the dataset. To do so, the Dockerfile relies on the use of build arguments
# and the copying of additional scripts from the directory of the robot that
# is being built.
#
# Build arguments
# ---------------
# APT_PACKAGES: a space-delimited list of missing packages that should be installed
# via apt
# BUILD_COMMAND: the command that should be used to build the Catkin workspace.
#   By default, catkin_make is used, but one may also use "catkin build"
#   instead as a means of avoiding certain build issues.
# DISTRO: specifies the ROS distribution that should be used by the base image
# DIRECTORY: specifies the directory that provides files for the robot
# ROSINSTALL_FILENAME: the name of the file that provides a .rosinstall for this
#   system
#
# References
# ----------
# * http://blog.fx.lv/2017/08/running-gui-apps-in-docker-containers-using-vnc
# * https://qxf2.com/blog/view-docker-container-display-using-vnc-viewer
# * https://github.com/ConSol/docker-headless-vnc-container/blob/master/src/ubuntu/install/libnss_wrapper.sh
# * https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-vnc-on-ubuntu-18-04
# * https://hackernoon.com/installation-of-vnc-server-on-ubuntu-1cf035370bd3
# * https://www.tecmint.com/install-and-configure-vnc-server-on-ubuntu
# * https://stackoverflow.com/questions/48601146/docker-how-to-set-tightvncserver-password
ARG DISTRO

# NOTE: We need to install the cmake_modules to avoid some build failures
# that are due to unspecified dependencies.
# (https://github.com/ros-industrial/industrial_calibration/issues/50)
# supervisor
FROM ros:${DISTRO} AS main
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PATH "/opt/rosqual/bin:${PATH}"
ARG COMMON_ROOTFS
COPY "${COMMON_ROOTFS}" /
WORKDIR /ros_ws
ENTRYPOINT ["/ros_ws/entrypoint.sh"]
CMD ["/bin/bash"]

RUN apt-get update \
 && /bin/bash -c "if [ \"${ROS_DISTRO}\" == \"melodic\" ]; then apt-get install -y libssl1.0.0; fi" \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# removed apt packages [conflicts with pyenv python/pip install]
# * python-catkin-tools
# * python-openssl
# * python-pip

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      "ros-${ROS_DISTRO}-cmake-modules" \
      apt-transport-https \
      apt-utils \
      build-essential \
      bzip2 \
      ca-certificates \
      clang \
      cmake \
      curl \
      curl \
      distro-info-data \
      g++ \
      gcc \
      git \
      less \
      libbz2-dev \
      libcurl3-gnutls \
      libffi-dev \
      liblzma-dev \
      libncurses5-dev \
      libncursesw5-dev \
      libreadline-dev \
      libsqlite3-dev \
      libssl-dev \
      llvm \
      mercurial \
      openssl \
      software-properties-common \
      tk-dev \
      tmux \
      vim \
      wget \
      xz-utils \
      zlib1g-dev \
 && echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list \
 && wget http://packages.osrfoundation.org/gazebo.key -O - | apt-key add - \
 && echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros-latest.list \
 && wget http://packages.ros.org/ros.key -O - | apt-key add - \
 && apt-get update \
 && curl -L https://github.com/pyenv/pyenv-installer/raw/4164fced49af78c6275cb436c64369eb39c6acb1/bin/pyenv-installer | bash \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# install a fixed version of python, pip, and some important packages
ENV PYENV_ROOT "/root/.pyenv"
ENV PATH="/root/.pyenv/bin:$PATH"
RUN /opt/rosqual/bin/install_python

# install vncserver
RUN apt-get update \
 && export DEBIAN_FRONTEND=noninteractive \
 && apt-get install -y --no-install-recommends\
      supervisor \
      vnc4server \
      xfce4 \
      xfce4-goodies \
      xfce4-terminal \
      xserver-xorg-core \
      xterm \
      xvfb \
      x11vnc \
      dbus-x11 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir ~/.vnc \
 && /bin/bash -c "echo -e 'password\npassword\nn' | vncpasswd"
ENV TINI_VERSION v0.9.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /bin/tini
RUN chmod +x /bin/tini \
 && apt-add-repository universe \
 && apt-get update && apt-get install -y ros-"${ROS_DISTRO}"-desktop-full

ARG CUDA_VERSION="0"
ENV CUDA_VERSION ${CUDA_VERSION}
RUN install_cuda_"${ROS_DISTRO}"
ENV CUDA_HOME /usr/local/cuda
ENV LD_LIBRARY_PATH "${LD_LIBRARY_PATH}:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
ENV PATH "${PATH}:${CUDA_HOME}/bin"

# apt packages
# Should not use --no-install-recommends argument because we need some of the package dependencies
ARG APT_PACKAGES
RUN apt-get install -y ${APT_PACKAGES} \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# build package
ARG DIRECTORY
ARG ROSINSTALL_FILENAME
COPY "${DIRECTORY}/${ROSINSTALL_FILENAME}" /.dockerinstall/
COPY "${DIRECTORY}/docker" /.dockerinstall/
RUN do_preinstall
RUN mv /.dockerinstall/${ROSINSTALL_FILENAME} /ros_ws/${ROSINSTALL_FILENAME} \
 && apt-get update \
 && wstool init -j8 src ${ROSINSTALL_FILENAME} \
 && rosdep update \
 && rosdep install -i -y -r --from-paths src \
      --ignore-src \
      --skip-keys="python-rosdep python-catkin-pkg python-rospkg" \
      --rosdistro="${ROS_DISTRO}" \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN do_prebuild

ARG BUILD_COMMAND="catkin_make -DCMAKE_EXPORT_COMPILE_COMMANDS=1"
RUN eval "$(pyenv init --path)" \
 && eval "$(pyenv init -)" \
 && eval "$(pyenv virtualenv-init -)" \
 && . /opt/ros/${ROS_DISTRO}/setup.sh \
 && eval "${BUILD_COMMAND}"

RUN do_postbuild
