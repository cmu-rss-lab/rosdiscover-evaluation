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


Dependencies
------------

* Python 3.9.5


Installation
------------

* clone the repo
* create a `pipenv` for the directory and execute all following commands in the pipenv shell
* call `./scripts/setup`

.. code::

  $ git submodule update --init --recursive
  $ pipenv --python 3.9 install
  $ ./scripts/setup


Usage
-----

* call `make <bug-id>` (e.g., `make autoware-01`) to create an image. `make all` will create all bug images
* call `run_rosdiscover <bug-id>` to launch rosdiscover on the given bug id (does not call `recover`)
