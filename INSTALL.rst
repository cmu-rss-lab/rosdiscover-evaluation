Installation Instructions
=========================

This document provides instructions for installing this replication package and is split into two parts:
(a) the installation of ROSDiscover, its dependencies, and the executable harness that are used to run the experiments;
and (b) the installation of the Docker images used in the evaluation dataset.
Users should follow the instructions for installing (a) before proceeding to install (b).



1. Prerequisites
----------------

1.1. Docker
...........

Before continuing, `Docker <https://www.docker.com>`_ 17.05 or higher must be installed on your machine.
The following command can be used to check the version of Docker that you have installed:

.. code::

  $ docker --version
  Docker version 20.10.11, build dea9396

Older versions of Docker do not support `multi-stage builds <https://docs.docker.com/develop/develop-images/multistage-build/>`_ and will
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

The images provided by this repository are known to work with macOS and several Linux distributions (Ubuntu, Arch), but are untested on Windows.


1.2. Command-Line Utilities
...........................

* `jq_ <https://stedolan.github.io/jq>`_ (can be installed via, e.g., :code:`apt install jq` on Ubuntu, or :code:`brew install jq` on macOS).



2. Software & Experiment Harness
--------------------------------

2.1. Approach A (Preferred): Docker
...................................


2.2. Approach B (Preferred): Native (pyenv + pipenv)
....................................................



3. Evaluation Dataset
---------------------



4. Confirming your installation
-------------------------------

TODO: add some simple steps to check that things were installed successfully
