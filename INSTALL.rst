Installation Instructions
=========================

This document provides instructions for installing this replication package and is split into two parts:
(a) the installation of ROSDiscover, its dependencies, and the executable harness that are used to run the experiments;
and (b) the installation of the Docker images used in the evaluation dataset.
Users should follow the instructions for installing (a) before proceeding to install (b).


1. Prerequisites
----------------

**This replication package is known to work with several Linux distributions, including Ubuntu and Arch,
but is untested on Windows and macOS.**


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

After installation, be sure to follow the
`post-installation instructions <https://docs.docker.com/engine/install/linux-postinstall>`_
(e.g., adding your user account to the `docker` group) to avoid common
issues (e.g., requiring `sudo` to run `docker` commands).


1.2. Command-Line Utilities
...........................

* `jq <https://stedolan.github.io/jq>`_ (can be installed via, e.g., :code:`apt install jq` on Ubuntu).


1.3. Disk Space
...............

Note that to install the replication package in its entirety, you will require just under 100 GB of disk space.



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

Once Python 3.9.5 has been installed, you should install pipenv.
`Pipenv <https://pypi.org/project/pipenv>`_ is a package manager for Python that allows you to install dependencies into a virtual environment without interfering with your system's Python installation.
To install pipenv, you can execute the following:

.. code:: command

  $ python -m pip install --user pipenv

Once installed, ensure that :code:`~/.local/bin` is added to your path (e.g., by editing your :code:`~/.bashrc` or :code:`~/.profile`).

Next, you can install ROSDiscover, its dependencies, and the experiment runner via pipenv by executing the following at the root of the replication package:

.. code:: command

  $ pyenv local 3.9.5
  $ pipenv install --python 3.9.5

Finally, you will need to install the ROSDiscover C++ static analysis tool by executing the following at the root of the replication package:

.. code:: command

   $ make -C deps/rosdiscover-cxx-recover/docker


3. Evaluation Dataset
---------------------

Once you have installed the experiment harness according to the instructions above, you will need to install the Docker images for each of the subject systems.
Note that this step will install require slightly under 100 GB of disk space.
Below we present two methods for installing the evaluation dataset:
(3.1) installing prebaked images, the preferred method for replication;
and (3.2) building images from scratch.


3.1. Approach A (Preferred Method): Installing prebuilt images
..............................................................

The preferred approach to installing the evaluation dataset is to install the Docker images using the :code:`images.tar.gz` file included in this replication package.
Using this approach will ensure that you run the experiments using exactly the same images that were used in the original paper submission.
In comparison, building the images from scratch may lead to slightly different images for reasons that are difficult to control (e.g., changes to :code:`apt/rosdep` packages, etc.).

The prebuilt Docker images can be installed on Linux using the command below.

.. code:: command

   $ gunzip -c images.tar.gz | docker load


After this step, you may wish to delete the :code:`images.tar.gz` to save disk space (after validating your installation following the instructions at the end of this document).

.. code::

   $ rm images.tar.gz


3.2. Approach B: Building images from scratch
.............................................

To build all of the Docker images for the replication package from scratch, you can execute the appropriate commands shown below.
If you installed the experiment harness via Docker, you should follow the commands prefixed with :code:`(docker)`.
Alternatively, if you installed the experiment harness natively via pipenv, you should follow the commands prefixed
with :code:`(native)`.

Be aware that building all images from scratch will take several hours depending on your compute hardware and network connection.

.. code:: command

   (docker) $ docker/run.sh build recovery all
   (docker) $ docker/run.sh build detection all

   (native) $ pipenv run build recovery all
   (native) $ pipenv run build detection all

Instead, you may also build the image for an individual experiment as shown below.
:code:`build recovery husky` will build the Docker image used in RQ1 and RQ2 for Husky.
:code:`build detection autoware-01` will build the Docker image used in RQ3 for Autoware-01.

.. code:: command

   (docker) $ docker/run.sh build recovery husky
   (docker) $ docker/run.sh build detection autoware-01

   (native) $ pipenv run build recovery husky
   (native) $ pipenv run build detection autoware-01

A list of all of the available systems can be obtained using the :code:`list` command as follows:

.. code:: command

  (docker) $ docker/run.sh list
  (native) $ pipenv run list


4. Confirming your installation
-------------------------------

The :code:`check-install` command, shown below, can be used to perform some basic checks of your installation, as shown below.

.. code:: command

    (docker) $ docker/run.sh check-install
    (native) $ pipenv run check-install

    Is jq installed? Yes (/usr/bin/jq)

    Is rosdiscover-cxx-recover installed? Yes

    The following evaluation dataset images have been successfully installed:
    * rosdiscover-experiments/autoware:84169473a3f72aea8a400464f5b673f3c77c6b8c
    * rosdiscover-experiments/autoware:fc8f691c70bf62a3de0f7448d9490b2e9385e6c4
    * rosdiscover-experiments/autoware:842990d9aca4f09004f3e88402d94ec2bbd339ee
    * rosdiscover-experiments/autoware:939ef1836bcdf0ff2a6c98d1c1ced940b0e242dd
    * rosdiscover-experiments/fetch:v0.8.3
    * rosdiscover-experiments/autorally:7b36814b5b2938345028a26381f96b5b625d0219
    * rosdiscover-experiments/husky:dc8169b6b7b9cfe37497f222adbe5f20bb83495a
    * rosdiscover-experiments/autoware:5f30cabe3aea301a211951cd288357bb170199de
    * rosdiscover-experiments/autoware:216269d752f232634acca6c3307c9af5c97cb17e
    * rosdiscover-experiments/autorally:5366f48da3ff6b19bf493d3aed39f37a02c950e6
    * rosdiscover-experiments/autorally:autorally-02-buggy
    * rosdiscover-experiments/husky:dc6750e916cfecc0fbb943183a5a671950f593a3
    * rosdiscover-experiments/autorally:7a49fbf584d5d14700d10a7a5d6226fa76ab30ee
    * rosdiscover-experiments/autoware:86f74272b0d933abb4b5d4e0a28802592843f4f1
    * rosdiscover-experiments/autoware:47d36ea2c3eff9fb0161b3a14097b70450b2c1b6
    * rosdiscover-experiments/autoware:4b2f608a2189f2284c6f9923ee88b983f28adb6f
    * rosdiscover-experiments/autorally:6ddb07745dc93e62a6386c83f5304147a98a9696
    * rosdiscover-experiments/husky:husky-02-fixed
    * rosdiscover-experiments/husky:husky-02-buggy
    * rosdiscover-experiments/autorally:autorally-02-fixed
    * rosdiscover-experiments/autoware:2a3f292eb451ac946959a3a20490427f0d2f764d
    * rosdiscover-experiments/husky:0.4.10
    * rosdiscover-experiments/autorally:a47a173290a175fa9ed1eb2b635afda25574bc63
    * rosdiscover-experiments/turtlebot:fc0e1b8d6e8b0f22a69d4958a5e073a48d87e291
    * rosdiscover-experiments/autorally:autorally-01-fixed
    * rosdiscover-experiments/autorally:3ae64dad2107baccac836b70f80c2bb4bc8669cd
    * rosdiscover-experiments/autoware:30eed1453e97eb4beb7b696ff22f5312ad80f5f6
    * rosdiscover-experiments/autoware:c2a090dec2101be2788ecb607102fa9210e24737
    * rosdiscover-experiments/husky:23c259f3340fbab901d3fe5d8fd6577e99d6e430
    * rosdiscover-experiments/autoware:f1fb9e205ca3d449a2e96f0f3409f9fd2d84ad8d
    * rosdiscover-experiments/autorally:autorally-03-buggy
    * rosdiscover-experiments/husky:husky-04-buggy
    * rosdiscover-experiments/husky:husky-06-fixed
    * rosdiscover-experiments/autoware:e9d6d6f8762457249ccb497680cf838b5a33d3e4
    * rosdiscover-experiments/autoware:0583e6d128450b2c567732cb9a00b828af7cd93e
    * rosdiscover-experiments/autorally:d1c56c0b11a35d573ef00c4276d5ba3e668728ac
    * rosdiscover-experiments/husky:97c5280b151665704f8f8e3beecb3e6e89ea14ae
    * rosdiscover-experiments/autorally:279c6642e5547876beeb536cced74661c8e46b50
    * rosdiscover-experiments/autoware:2fbad6d64f9d71e4b1b5e1de9008ca63f3b44fa1
    * rosdiscover-experiments/husky:3796317c73f184d767b1a74f7d58d0cc5b3f84fe
    * rosdiscover-experiments/autorally:c2692f2
    * rosdiscover-experiments/autoware:6a7d1b9f66fd353eb5c6ad8df942c433fff8e2a1
    * rosdiscover-experiments/turtlebot:3e32933c829e308600707a9f971334d13d1cbe19
    * rosdiscover-experiments/husky:husky-04-fixed
    * rosdiscover-experiments/mavros:mavros-02-buggy
    * rosdiscover-experiments/autoware:a2ab41dafe76579a76ad23f92f8f4992b701433b
    * rosdiscover-experiments/turtlebot:e799e45abdfe3106ac105ce21dd43283381ba180
    * rosdiscover-experiments/autorally:autorally-04-buggy
    * rosdiscover-experiments/autorally:autorally-04-fixed
    * rosdiscover-experiments/autoware:8bf1c47fbc18a0303fda23c601dfe959a3afbc41
    * rosdiscover-experiments/autorally:autorally-03-fixed
    * rosdiscover-experiments/autoware:static
    * rosdiscover-experiments/autoware:37b9feba82e6a6fabfa689fcf9d210c3c8f287f6
    * rosdiscover-experiments/autoware:6428d5fb34b961fd37da212bdb068f77ae99f25f
    * rosdiscover-experiments/husky:husky-06-buggy
    * rosdiscover-experiments/turtlebot:2.4.2
    * rosdiscover-experiments/autoware:92d9732112467fb2e7d7f66da56be51ba746915b
    * rosdiscover-experiments/autorally:autorally-01-buggy
    * rosdiscover-experiments/mavros:mavros-02-fixed
    * rosdiscover-experiments/turtlebot:b26d199a18d350e72495c4d8935e5b1ccc64d75a
    * rosdiscover-experiments/autoware:3db7e153dc111682857ffd089018b92b2eed1786
    * rosdiscover-experiments/husky:8afd94b417f33e6be6c8b7196ad9ca66260250c7

    The following evaluation dataset images are missing:

