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

ROSDiscover, its dependencies, and the scripts used to conduct the experiments can be installed either via Docker (2.1), the preferred method for replication of results, or natively (2.2) via pipenv.
We provide instructions for both of these approaches below.


2.1. Approach A (Preferred Method): Docker
..........................................

To install the Docker-based experiment harness, which includes ROSDiscover and all other necessary software, you should run:

.. code::

   $ docker/setup.sh


2.2. Approach B: Native (pipenv)
................................

Alternatively, to install the necessary software and experiment harness natively, you will first need to install both (a) Python 3.9 or greater and (b) pipenv.
Since Python 3.9 or greater is not provided as the system Python installation on many distributions, we optionally recommend using pyenv to automatically install a standalone Python 3.9 without interfering with the rest of your system.

`pyenv <https://github.com/pyenv/pyenv>`_ is a tool for managing multiple Python installations.
Be careful to ensure that you have installed all of pyenv's prequisites by following these instructions: https://github.com/pyenv/pyenv/wiki/Common-build-problems.
Once you have installed the dependencies for pyenv, you can install pyenv itself by executing the following:

.. code:: command

  $ curl https://pyenv.run | bash

You should then check that your :code:`~/.profile` sources :code:`~/.bashrc`.
Once you have ensured that is the case, you should add the following lines to :code:`~/.profile` immediately prior to the point where :code:`~/.bashrc` is sourced.

.. code:: command

  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init --path)"

Additionally, you should add the following lines to your :code:`~/.bashrc`:

.. code:: command

  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"

After making the above changes, you should restart your shell so that the changes in :code:`~/.profile` and :code:`~/.bashrc` take effect.
You can then install Python 3.9.5 via the following:

.. code:: command

  $ pyenv install 3.9.5


3. Evaluation Dataset
---------------------



4. Confirming your installation
-------------------------------

TODO: add some simple steps to check that things were installed successfully
