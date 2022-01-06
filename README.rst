ROS Discover Evaluation
=======================

This is the replication package for the paper, **ROSDiscover: Statically Detecting Run-Time Architecture Misconfigurations in Robotics Systems.**
This package is has been anonymized to the best of our ability for the purpose of technical track submission.

To replicate the results in this package, you must build several Docker images.
In the real replication package, we will bundle those Docker images in a tar archive, but due to practical limitations (and > 100GB file size),
you will need to build them in this anonymized replication package.

The structure of this package is as follows:

.. code::
  
  - architecture-style/    The definition of the ROS architeture style used for analysis.
  - deps/                  Contains the code that the evaluation pacakges uses.
    |- rosdiscover/        The code for the implementation of the rosdiscover system
    |                      evaluated in the paper
    |- roswire/            The code for the layer used for interacting with ROS
    |                      docker images
    |- rosdiscover-cxx-extract/
    |                      The code for static analysis
  - docker/                Files used for building docker images used in the experiments
  - experiments/           Data for setting up the experiments, and the results we got
    |- detection/          Experiments that we used in RQ3
    |- recovery/           Experiments we used in RQ1 and RQ2
  - results/               Contains raw and processed results from running the scripts
    |- DataAnalysis.ipynb  A Jupyter notebook used for processing the results
    |- data/               Various CSV files used for summarizing data for the paper
    |  |- RosTopicBugs - Bug Data Set.csv
    |                      The misconfiguration bug dataset contributed in the paper
    |- detection/          Results for the detection experiments
    |- recovery/           Results for the recovery experiments
  - rootfs/                Contains files that get put in the docker images
  - scripts/               Python scripts for running and analyzing the experiments
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
.....

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

  $ pyenv install 3.9.5

Pipenv
~~~~~~

`Pipenv <https://pypi.org/project/pipenv/>`_ is a package manager for Python that allows you to install dependencies into a
pyenv environment. To install pipenv, you can execute the following:

.. code:: command

  $ python -m pip install --user pipenv
  
Once installed, ensure that `~/.local/bin` is added to your path (by editing you ~/.bashrc). To run the scripts in this package, you need to install some dependencies. This can be done by first entering a pipenv shell, and then installing the dependencies:

.. code:: command

  $ pipenv shell
  (rosdiscover-evaluation)$ pipenv install
  Installing dependencies from Pipfile.lock (6070d0)...
  
Exit the pipenv shell with:

.. code:: command

  $ (rosdiscover-evaluation)$ exit
  
You do not need to enter the pipenv shell again for future commands, since those will be using pipenv run

Replicating results for the paper
=================================
To aid in replicating the results of the research, we have provided a set of scripts that ease each set, along with an experiment definition or
each experiment cast. The defitition is defined using YAML, and provides all the information for building containers, recovering nodes, extracting
and checking architectures, and detecting misconfigurations. In these instructions (except for misconfigurtion bug detection) we will use `autorally`
as an example, with the experiment defined in `experiments/recovery/subjects/autorally/experiment.yml`.

You may run the experiments from the host, using the python directly with Python set up as above, or by optionally
using the `rosdiscover/evaluation` Docker container that encapsulates this inside its own Docker container. NOTE: In
order for this to work, the container will need to connect to the Docker that is running on the host. In the
instructions below, we give two versions of each command. One, prefixed by `(directly)$` is how to run the command
from the host; thoe other `(container)$` is how to run the command using the provided helper script that connects to
the evaluation Docker container. Building this container is shown in the optional step below.

Optional: Use provided docker evaluation image
----------------------------------------------

For faster startup, we have provided a docker image for running the evaluation scripts, and a shell script for
connecting to it. To build the docker image, you can either use the saved image data in this package:

.. code::

  $ gunzip containers/evaluation.tgz | docker load

Or build it from scratch:

.. code::

  $ docker/setup.sh

In both cases, you should now have an image `rosqual/icsa22-evaluation:runner`. You can get a list of the commands that can
be run in the docker version, and the available experiments, by running:

.. code::

  (container)$ ./run.sh help
  (container)$ ./run.sh list

Build the Docker containers for RQ1 and RQ2
-------------------------------------------

Our analysis requires robot software to be installed in Docker containers.
So,to run the experiments, the containers first need to be built.

NOTE: Building the images takes some time. For convenience, we have provided saved images in the `images/`
directly. You can load all of these by doing:

.. code::

  $ gunzip images/rosdiscover-experiments.tgz | docker load

Alternatively, you can build the experiment images from scratch. In the examples

We provide a script that does this for all our experiments - it generates a Dockerfile and the uses Docker to build the container. To build the container:

.. code::

  (directly)$ pipenv run scripts/build-images.py recovery autorally
  (container)$ ./run.sh build recovery autorally
  2021-11-10 18:18:03.271 | INFO     | __main__:build_image:38 - apt_packages_arg: cmake-curses-gui cutecom doxygen libglademm-2.4-1v5 libglademm-2.4-dev libgtkglextmm-x11-1.2 libgtkglextmm-x11-1.2-dev libgtkmm-2.4-1v5 libraw1394-11 libusb-1.0-0 libusb-dev openssh-server synaptic texinfo ros-melodic-rqt-publisher ros-melodic-gazebo-ros-pkgs
  2021-11-10 18:18:03.278 | INFO     | __main__:build_image:53 - building image: docker build -f /code/docker/Dockerfile --build-arg COMMON_ROOTFS=docker/rootfs --build-arg CUDA_VERSION='11-4' --build-arg APT_PACKAGES='cmake-curses-gui cutecom doxygen libglademm-2.4-1v5 libglademm-2.4-dev libgtkglextmm-x11-1.2 libgtkglextmm-x11-1.2-dev libgtkmm-2.4-1v5 libraw1394-11 libusb-1.0-0 libusb-dev openssh-server synaptic texinfo ros-melodic-rqt-publisher ros-melodic-gazebo-ros-pkgs' --build-arg BUILD_COMMAND='catkin build -DCMAKE_EXPORT_COMPILE_COMMANDS=1' --build-arg DIRECTORY=experiments/recovery/subjects/autorally --build-arg ROSINSTALL_FILENAME=pkgs.rosinstall --build-arg DISTRO=melodic . -t rosdiscover-experiments/autorally:c2692f2
  ...
  
At the conclusion of this, you should have a docker image `rosdiscover-evaluation/autorally:c2692f2` built.


Run recovery of all nodes in images for RQ1
-------------------------------------------

To run the component model recovery experiments described in RQ1, you should use the `recover-node-models.py` script provided in the experimental scripts directory.
The script simply takes the name of a subject system for RQ1 and emits a set of component models (in JSON) form, along with a summary of the success of the overall process (recovered-models.csv), describing the number of API calls that were found and successfully resolved for each individual node in that subject system.

.. code::

  (directly)$ pipenv run scripts/recover-node-models.py autorally
  (directly)$ pipenv run scripts/recover-node-models.py autoware
  (directly)$ pipenv run scripts/recover-node-models.py fetch
  (directly)$ pipenv run scripts/recover-node-models.py husky
  (directly)$ pipenv run scripts/recover-node-models.py turtlebot

  (container)$ ./run.sh recover-node-models autorally
  (container)$ ./run.sh recover-node-models autoware
  (container)$ ./run.sh recover-node-models fetch
  (container)$ ./run.sh recover-node-models husky
  (container)$ ./run.sh recover-node-models turtlebot


Derive and check architecture for RQ2
-------------------------------------

The experimental setups for RQ2 are in the `experiments/recovery/subjects` directories. We currently report results for recovery in `turtlebot`, `autorally`, and  `husky`. RQ2 consists of two phases followed by checking and comparison of results. All the examples will be given or `autorally` but should be the same for the other subjects. All commands are executed in the root directory of this package.

1. Derived the ground truth by observing the running system.

.. code::

   (directly)$ pipenv run scripts/observe-system.py autorally
   (container)$ ./run.sh observe autorally
   
This will take a while to run because it needs to start the robot, start a mission, and then observe the architecture multiple times. In the end, a YML representation of the architecture will be placed in `experiments/recovery/subjects/autorally/observed.architecture.yml`. 

To check the architecure

2. Run ROSDiscover to statically recover the system.

.. code::

  (directly)$ pipenv run scripts/recover-system.py recovery autorally
  (container)$ ./run.sh recovery autorally
  INFO: reconstructing architecture for image [rosdiscover-experiments/autorally:c2692f2]
  ...
  INFO: applying remapping from [/camera/left/camera_info] to [/left_camera/camera_info]
  INFO: applying remapping from [/camera/right/camera_info] to [/right_camera/camera_info]
  INFO: statically recovered system architecture for image [rosdiscover-experiments/autorally:c2692f2]
  
This will process the launch files supplied in the `experiment.yml` and produce the architecture in `experiments/recovery/subjects/autorally/recovered.architecture.yml`. The first time this is run it may take some time because it needs to statically analyze the source for the nodes mentioned in the launch files, but thereafter those results are cached and the analysis will run more quickly.

3. Check and compare the architectures of the observed and recovered systems. This involves three steps.
  a. Produce and check the architecture of the observed system

.. code::

  (directly)$ pipenv run scripts/check-architecture.py observed experiments/recovery/subjects/autorally/experiment.yml
  (container)$ ./run.sh check observed recovery autorally
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

  (directly)$ pipenv run scripts/check-architecture.py recovered experiments/recovery/subjects/autorally/experiment.yml
  (container)$ ./run.sh check recovered recovery autorally
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

  (directly)$ pipenv run scripts/compare-recovered-observed.py autorally
  (container)$ ./run.sh compare autorally

The comparison output is placed in `experiments/recovery/subjects/autorally/compare.observed-recovered.log`. The analyzed results used in the paper are in `experiments/recovery/subjects/autorally/observed.recovered.compare.csv`.


If you look at the file `experiments/recovery/subjects/autorally/observed.recovered.compare.csv` (**TODO: Add link to result in repo**), it is divided into five sections. 

1. Observed architecture summary. This summarizes the observed architceture. It is a summarization of `experiments/recovery/subjects/autorally/observed.architecture.acme`
2. Recovered architecture summary. This summarizes the recovered architecture. It is a summarization of `experiments/recovery/subjects/autorally/recovered.architecture.acme` 
3. Provenance information. This summarizes the component models used in recovery that were handwritten and recovered.
4. Side-by-side comparison: This gives a side by side comparison of the details of the architecture, giving topics etc that were observed for a node, those that were recovered. Upper case elements are those that appear in both the observed and recovered architectures, those in lower case only appear in one.
5. Differences: A summary of the statistics for over-approximation/under-approximation for the whole system (not that in `observed.recovered.compare.csv` we divide these numbers into handwritten and recovered, and only use the recovered metrics in the paper.

Run configuration mismatch bug detection for RQ3
------------------------------------------------

To run configuration mismatch bugs for RQ3 involves building another set of Docker images that build the system representing the system at the time the misconfiguration was extant and the time at which it was fixd. Like the other RQs, we use use the same scripts for building these images. We will use the example of the `autorally-01` bug which is an error that was introduced into the `autorally_core/launch/stateEstimator.launch` file that incorrectly remapped a topic. The format of the experiment definition for detection replciation is different to the other experiment defintions, containing information on how to build the buggy and fixed docker images, the errors that are expected to be found, and defintion of a reproducer node that guarantees use of the broken connector. To build the images:

.. code::

  (directly)$ pipenv run scripts/build-images.py detection autorally-01
  (container)$ ./run.sh build detection autorally-01
  ...
  
To check that the error is detected in the buggy version, and disappears in the fixed version:

.. code::

  (directly)$ pipenv scripts/check-architecture.py detected detection autorally-01
  (container)$ ./run.sh check detected detection autorally-01

One complication for replicating RQ3 is that it sometimes wasn't possible to restore the version of the robot software at the time that the bug was extant. Instead, we forward ported these bugs into the docker images from RQ1&2. Unfortunately, seeding the bugs is currently not yet as automated as the rest of the replication package - the docker images will need to be built explicitly. For the cases in which we needed to forward port, we included a separate experiment definition (e.g., `experiment-reproduced.yml` and a Dockerfile each to build the buggy version that seeds the error into the correct containers, and the fixed version (in cases it needed to be different from the original version). To build these requires using the Docker command explicitly, e.g., for `husky-04`:

.. code::

  $ docker build -t rosdiscover-evaluation/husky:husky-04-buggy -f experiments/detection/subjects/husky-04/Dockerfile-reproduce-error experiments/detection/subjects/husky-04/
  $ docker build -t rosdiscover-evaluation/husky:husky-04-fixed -f experiments/detection/subjects/husky-04/Dockerfile-reproduce-fixed experiments/detection/subjects/husky-04/
  
Not that the name of the image (e.g., `rosdiscover-evaluation/husky:husky-04-fixed`) has to be the same as the one referred to in `experiment-reproduced.yml`.

The misconfiguration detection can be done in the same was as above (i.e., `check-architecture.yml detected .../experiment-reproduced.yml`).

Results Data
============

Raw results
-----------

The replication package also provides results that we used in the paper. Data for each detection case is in

.. code::

  results/detection/subjects/[autorally-N, autoware-N, ...]

For each case where we could duplicate the misconfiguration, there is a `buggy.architecture.[yml,acme]`,
`fixed.architecture/[yml,acme]` that define the architecture recovered and an `error-report.csv` that reports whether
we captured the misconfiguration error or not.

The results for the recovery case is in:

.. code::

  results/recovery/subjects/[autorally, husky, ...]

Each case has the following files:

.. code::

  [recovered,obeserved].architecture.[yml,acme]   - recovered and observed architetures
  compare.observed-recovered.log                  - a human readable summary of the comparison
  observed.recovered.[compare,errors].csv         - a CSV version of the comparison results,
                                                    with errors detected
  recovery.rosdiscover.yml                        - a script generated config file passed to rosdiscover
  recovered-models.csv                            - a list of models recovered for RQ1 and the accuracy
                                                    metrics

Processed Results and Data Analysis
-----------------------------------

The data collected for the experiments of RQ1 are in these files:

- results/data/RQ1 node model recovery results - autorally.csv
- results/data/RQ1 node model recovery results - autoware.csv
- results/data/RQ1 node model recovery results - fetch.csv
- results/data/RQ1 node model recovery results - husky.csv
- results/data/RQ1 node model recovery results - turtlebot.csv

The data collected for the experiments of RQ2 are in these files:

- results/data/RQ2 Observed Architecture - Comparison.csv
- results/data/RQ2 Observed Architecture - Models.csv
- results/data/RQ2 Observed Architecture - Node-Level Comparision.csv
- results/data/RQ2 Observed Architecture - Summary.csv

The data collected for the experiments of RQ3 is in: results/data/RosTopicBugs - RQ3 - Results Table.csv

The Jupyer Notebook in results/DataAnalysis.ipynb uses these results to aggregate them to produce the numbers in the paper. To run this analysis, the local system needs Python 3 with these packages:

- pandas (version 1.3.3)
- matplotlib (version 3.4.3)
- numpy (version 1.21.2)

The resulting files are directly read by our paper LaTeX sources.
