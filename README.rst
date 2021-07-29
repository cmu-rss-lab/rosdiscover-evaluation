ROS Discover Evaluation
=======================

Image Creation and Evaluation Infrastructure for ROS Discover


Dependencies
------------

* Python 3.9.5

Installation
------------

* clone the repo
* create a `pipenv` for the directory and execute all following commands in the pipenv shell
* call `make init`

Usage
------------

* call `make <bug-id>` (e.g., `make autoware-01`) to create an image. `make all` will create all bug images
* call `run_rosdiscover <bug-id>` to launch rosdiscover on the given bug id (does not call `recover`)
