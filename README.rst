ROS Discover Evaluation
=======================

This is the replication packagee for the paper: ROSDiscover: Discovering Architectural Misconfigurations through Static Analysis. THis package is currently anonymized to the bset of our ability.

To replicate the results in this packqage, you must build various docker files (in the real replication package we will provide docker images but for double blind evaluation you will beed to build them). The structure of the rpository is:

.. code::

  deps/                  Contains the code that the evaluation pacakges uses
  |- rosdiscover/        The code for the implementation of the rosdiscover system
  |                      evaluated in the paper
  |- roswire/            The code for the layer used for interacting with ROS
  |                      docker images
  |- rosdiscover-cxx-extract/
  |                      The code for static analysis
  docker/                Files used for building docker images used in the experiments
  experiments/           Data for setting up the experiments, and the results we got
  |- detection/          Experiments that we used in RQ3
  |- recovery/           Experiments we used in RQ2 
  rootfs                 Contains files that get put in the docker images
  scripts                Python scripts for running and analyzing the experiments
                         (see more below)
                         

Image Creation and Evaluation Infrastructure for ROS Discover


Prerequisites 
-------------

Docker
~~~~~~

Before you can use the images provided by the repo, make sure that `Docker
<https://www.docker.com/>`_ 17.05 or higher is installed on your machine.
Older versions of Docker do not support `multi-stage builds
<https://docs.docker.com/develop/develop-images/multistage-build/>`_ and will
be unable to build the images provided by this repository.
See the following for platform-specific instructions for installing Docker:

* `Installing Docker Engine on Ubuntu <https://docs.docker.com/engine/install/ubuntu>`_
* `Installing Docker Engine on Fedora <https://docs.docker.com/engine/install/fedora>`_
* `Install Docker Desktop on Mac <https://docs.docker.com/docker-for-mac/install>`_
* `Install Docker Desktop on Windows <https://docs.docker.com/docker-for-windows/install>`_

If using Linux, make sure to follow the
`post-installation instructions <https://docs.docker.com/engine/install/linux-postinstall>`_
(e.g., adding your user account to the `docker` group) to avoid common
issues (e.g., requiring `sudo` to run `docker` commands).

The images provided by this repository are known to work with
Mac OSX and several Linux distributions (Ubuntu, Arch), but are untested
on Windows.

Python
~~~~~~

The code in this project requires both Python 3.9+ and Poetry to be installed.
Since Python 3.9 or greater is not provided as the system Python installation on
many distributions, we optionally recommend using pyenv to automatically install
a standalone Python 3.9 without interfering with the rest of your system.


pyenv 
................

`pyenv <https://github.com/pyenv/pyenv>`_ is a tool for managing multiple Python installations.
Installation instructions for pyenv can be found at https://github.com/pyenv/pyenv-installer.
Once you have installed the dependencies for pyenv, you can quickly install
pyenv itself by executing the following:

.. code:: command

  $ curl https://pyenv.run | bash

You should then check that your :code:`~/.profile` sources :code:`~/.bashrc`.
Once you have ensured that is the case, you should add the following lines to
:code:`~/.profile` immediately prior to the point where :code:`~/.bashrc` is
sourced.

.. code:: command

  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init --path)"


Additionally, you should add the following lines to your :code:`~/.bashrc`:

.. code:: command

  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"

After making the above changes, you should restart your shell so that the changes
in :code:`~/.profile` and :code:`~/.bashrc` take effect. You can then install
Python 3.9.5 via the following:

.. code:: command

  $ pipenv install 3.9.5

* clone the repo
* create a `pipenv` for the directory and execute all following commands in the pipenv shell
* call `./scripts/setup`

.. code::

  $ git submodule update --init --recursive
  $ pipenv --python 3.9 install
  $ ./scripts/setup

Replicating results for the paper
================================

To aid in replicating the results of the research, we have provided a set of scripts that ease each set, along with an experiment definition or 
each experiment cast. The defitition is defined using YAML, and provides all the information for building containers, recovering nodes, extracting
and checking architectures, and detecting misconfigurations. In these instructions (except for misconfigurtion bug detection) we will use `autorally` 
as an example, with the experiment defined in `experiments/recovery/subjects/autorally/experiment.yml`. 

Build the Docker containers for RQ1 and RQ2
-------------------------------------------

Our analysis requires robot software to be installed in Docker containers. So, to run the experiments, the containers first need to be built. 
We provide a script that does this for all our experiments - it generates a Dockerfile and the uses Docker to build the container. To build the container:

.. code::

  $ pipenv run scripts/build-images.py experiments/recovery/subjects/autorally/experiment.yml
  2021-11-10 18:18:03.271 | INFO     | __main__:build_image:38 - apt_packages_arg: cmake-curses-gui cutecom doxygen libglademm-2.4-1v5 libglademm-2.4-dev libgtkglextmm-x11-1.2 libgtkglextmm-x11-1.2-dev libgtkmm-2.4-1v5 libraw1394-11 libusb-1.0-0 libusb-dev openssh-server synaptic texinfo ros-melodic-rqt-publisher ros-melodic-gazebo-ros-pkgs
  2021-11-10 18:18:03.278 | INFO     | __main__:build_image:53 - building image: docker build -f /code/docker/Dockerfile --build-arg COMMON_ROOTFS=docker/rootfs --build-arg CUDA_VERSION='11-4' --build-arg APT_PACKAGES='cmake-curses-gui cutecom doxygen libglademm-2.4-1v5 libglademm-2.4-dev libgtkglextmm-x11-1.2 libgtkglextmm-x11-1.2-dev libgtkmm-2.4-1v5 libraw1394-11 libusb-1.0-0 libusb-dev openssh-server synaptic texinfo ros-melodic-rqt-publisher ros-melodic-gazebo-ros-pkgs' --build-arg BUILD_COMMAND='catkin build -DCMAKE_EXPORT_COMPILE_COMMANDS=1' --build-arg DIRECTORY=experiments/recovery/subjects/autorally --build-arg ROSINSTALL_FILENAME=pkgs.rosinstall --build-arg DISTRO=melodic . -t rosdiscover-experiments/autorally:c2692f2
  ...
  
At the conclusion of this, you should have a docker image `rosdiscover-evaluation/autorally:c2692f2` built.

Run recovery of all nodes in images for RQ1
-------------------------------------------

Derive and check architecture for RQ2
-------------------------------------

The experimental setups for RQ2 are in the `experiments/recovery/subjects` directories. We currently report results for recovery in `turtlebot`, `autorally`, and  `husky`. RQ2 consists of two phases followed by checking and comparison of results. All the examples will be given or `autorally` but should be the same for the other subjects. All commands are executed in the root directory of this package.

1. Derived the ground truth by observing the running system.

.. code::

   $ pipenv run scripts/observe-system.py experiments/recovery/subjects/autorally/experiment.yml
   
This will take a while to run because it needs to start the robot, start a mission, and then observe the architecture multiple times. In the end, a YML representation of the architecture will be placed in `experiments/recovery/subjects/autorally/observed.architecture.yml`. 

To check the architecure

2. Run ROSDiscover to statically recover the system.

.. code::

  $ pipenv run scripts/recover-system.py experiments/recovery/subjects/autorally/experiment.yml
  INFO: reconstructing architecture for image [rosdiscover-experiments/autorally:c2692f2]
  ...
  INFO: applying remapping from [/camera/left/camera_info] to [/left_camera/camera_info]
  INFO: applying remapping from [/camera/right/camera_info] to [/right_camera/camera_info]
  INFO: statically recovered system architecture for image [rosdiscover-experiments/autorally:c2692f2]
  
This will process the launch files supplied in the `experiment.yml` and produce the architecture in `experiments/recovery/subjects/autorally/recovered.architecture.yml`. The first time this is run it may take some time because it needs to statically analyze the source for the nodes mentioned in the launch files, but thereafter those results are cached and the analysis will run more quickly.

3. Check and compare the architectures of the observed and recovered systems. This involves three steps.
  a. Produce and check the architecture of the observed system

.. code::

  $ pipenv run scripts/check-architecture.py observed experiments/recovery/subjects/autorally/experiment.yml 
  INFO: Writing Acme to /code/experiments/recovery/subjects/autorally/recovered.architecture.acme
  INFO: Writing Acme to /code/experiments/recovery/subjects/autorally/recovered.architecture.acme
  INFO: Checking architecture...
  Checking architecture...
  ...
  ground_truth_republisher  publishes to an unsubscribed topic: '/ground_truth/state'. But there is a subscriber(s) waypointFollower._pose_estimate_sub 
  with a similar name that subscribes to a similar message type. ground_truth_republisher was launched from unknown.
 
The result is placed in experiments/recovery/subjects/autorally/observed.architecture.acme
  
  b. Produce and check the architecture of the recovered system
  
.. code::

  $ pipenv run scripts/check-architecture.py recovered experiments/recovery/subjects/autorally/experiment.yml 
  INFO: Writing Acme to /code/experiments/recovery/subjects/autorally/recovered.architecture.acme
  INFO: Writing Acme to /code/experiments/recovery/subjects/autorally/recovered.architecture.acme
  INFO: Checking architecture...
  Checking architecture...
  ...
  ground_truth_republisher  publishes to an unsubscribed topic: '/ground_truth/state'. But there is a subscriber(s) waypointFollower._pose_estimate_sub 
  with a similar name that subscribes to a similar message type. ground_truth_republisher was launched from /ros_ws/src/autorally/autorally_gazebo/launch
  /autoRallyTrackGazeboSim.launch.

The result is placed in experiments/recovery/subjects/autorally/recovered.architecture.acme
  
  c. Compare the architectures
  
.. code::

  $ pipenv run scripts/compare-recovered-observed.py recovered experiments/recovery/subjects/autorally/experiment.yml 
  
The comparison output is placed in `experiments/recovery/subjects/autorally/compare.observed-recovered.log`. The analyzed results used in the paper are in `experiments/recovery/subjects/autorally/observed.recovered.compare.csv`.


If you look at the file `experiments/recovery/subjects/autorally/observed.recovered.compare.csv` (**TODO: Add link to result in repo**), it is divided into five sections. 

1. Observed architecture summary. This summarizes the observed architceture. It is a summarization of `experiments/recovery/subjects/autorally/observed.architecture.acme`
2. Recovered architecture summary. This summarizes the recovered architecture. It is a summarization of `experiments/recovery/subjects/autorally/recovered.architecture.acme` 
3. Provenance information. This summarizes the component models used in recovery that were handwritten and recovered.
4. Side-by-side comparison: This gives a side by side comparison of the details of the architecture, giving topics etc that were observed for a node, those that were recovered. Upper case elements are those that appear in both the observed and recovered architectures, those in lower case only appear in one.
5. Differences: A summary of the statistics for over-approximation/under-approximation for the whole system (not that in `observed.recovered.compare.csv` we divide these numbers into handwritten and recovered, and only use the recovered metrics in the paper.

Run configuration mismatch bug detection for RQ3
------------------------------------------------

Usage
-----

* call `make <bug-id>` (e.g., `make autoware-01`) to create an image. `make all` will create all bug images
* call `run_rosdiscover <bug-id>` to launch rosdiscover on the given bug id (does not call `recover`)
