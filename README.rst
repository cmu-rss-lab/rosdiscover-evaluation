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

Build the Docker containers for RQ1 and RQ2
-------------------------------------------

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

  
This will process the launch files supplied in the `experiment.yml` and produce the architecture in `experiments/recovery/subjects/autorally/recovered.architecture.yml`. The first time this is run it may take some time because it needs to statically analyze the source for the nodes mentioned in the launch files, but thereafter those results are cached and the analysis will run more quickly.

3. Check and compare the architectures of the observed and recovered systems.

.. code::

  # (a) Produce and check the architecture of the observed system
  $ pipenv run scripts/check-architecture.py observed experiments/recovery/subjects/autorally/experiment.yml 
  
  # The result is placed in experiments/recovery/subjects/autorally/observed.architecture.acme
  
  # (b) Produce and check the architecture of the recovered system
  $ pipenv run scripts/check-architecture.py recovered experiments/recovery/subjects/autorally/experiment.yml 
  
  # The result is placed in experiments/recovery/subjects/autorally/recovered.architecture.acme
  
  # (c) Compare the architectures
  $ pipenv run scripts/compare-recovered-observed.py recovered experiments/recovery/subjects/autorally/experiment.yml 
  
  # The comparison output is placed in experiments/recovery/subjects/autorally/compare.observed-recovered.log 
  # The analyzed results used in the paper are in experiments/recovery/subjects/autorally/observed.recovered.compare.csv


Run configuration mismatch bug detection for RQ3
------------------------------------------------

Usage
-----

* call `make <bug-id>` (e.g., `make autoware-01`) to create an image. `make all` will create all bug images
* call `run_rosdiscover <bug-id>` to launch rosdiscover on the given bug id (does not call `recover`)
