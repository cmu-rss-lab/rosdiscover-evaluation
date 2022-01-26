ROS Discover Evaluation
=======================

This is the replication package for the paper, **ROSDiscover: Statically Detecting Run-Time Architecture Misconfigurations in Robotics Systems.**


Contents
========

This replication package is structured as follows:

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


Replicating results for the paper
=================================

To aid in replicating the results of the research, we have provided a set of scripts that ease each set, along with an experiment definition or
each experiment cast. The defitition is defined using YAML, and provides all the information for building containers, recovering nodes, extracting
and checking architectures, and detecting misconfigurations. In these instructions (except for misconfigurtion bug detection) we will use `autorally`
as an example, with the experiment defined in `experiments/recovery/subjects/autorally/experiment.yml`.

You may run the experiments from the host, using the python directly with Python set up as above, or by optionally
using the `rosdiscover/evaluation` Docker container that encapsulates this inside its own Docker container. NOTE: In
order for this to work, the container will need to connect to the Docker that is running on the host. In the
instructions below, we give two versions of each command. One, prefixed by `(native)$` is how to run the command
from the host; thoe other `(container)$` is how to run the command using the provided helper script that connects to
the evaluation Docker container.

Aobtain a list of commands that can be executed inside the replication package by executing the :code:`help` command as shown below from the root of the replication package.

.. code::

  (docker) $ docker/run.sh help
  (native) $ pipenv run help

You can also obtain a list of all of the experiments using the :code:`list` command:

.. code::

  (native) $ docker/run.sh list
  (native) $ pipenv run list


Run recovery of all nodes in images for RQ1
-------------------------------------------

To run the component model recovery experiments described in RQ1, you should use the `recover-node-models.py` script provided in the experimental scripts directory.
The script simply takes the name of a subject system for RQ1 and emits a set of component models (in JSON) form, along with a summary of the success of the overall process (recovered-models.csv), describing the number of API calls that were found and successfully resolved for each individual node in that subject system.

.. code::

  (docker)$ docker/run.sh recover-node-models autorally
  (docker)$ docker/run.sh recover-node-models autoware
  (docker)$ docker/run.sh recover-node-models fetch
  (docker)$ docker/run.sh recover-node-models husky
  (docker)$ docker/run.sh recover-node-models turtlebot

  (native)$ pipenv run scripts/recover-node-models.py autorally
  (native)$ pipenv run scripts/recover-node-models.py autoware
  (native)$ pipenv run scripts/recover-node-models.py fetch
  (native)$ pipenv run scripts/recover-node-models.py husky
  (native)$ pipenv run scripts/recover-node-models.py turtlebot


Derive and check architecture for RQ2
-------------------------------------

The experimental setups for RQ2 are in the `experiments/recovery/subjects` directories. We currently report results for recovery in `turtlebot`, `autorally`, and  `husky`. RQ2 consists of two phases followed by checking and comparison of results. All the examples will be given or `autorally` but should be the same for the other subjects. All commands are executed in the root directory of this package.

Note the for convenience, we provide a shell script that automates all the steps below. It assumes that all the
images have been prebuilt as described above. To run this:

.. code::

  (docker)$ docker/run.sh rq2 [autorally | husky | turtlebot]
  (native)$ scripts/rq2.sh [autorally | husky | turtlebot]

If no arguments are given, the script will run through all three cases.


1. Derived the ground truth by observing the running system.

.. code::

      (docker)$ docker/run.sh observe autorally
      (native)$ pipenv run scripts/observe-system.py autorally

This will take a while to run because it needs to start the robot, start a mission, and then observe the architecture multiple times. In the end, a YML representation of the architecture will be placed in `experiments/recovery/subjects/autorally/observed.architecture.yml`.

To check the architecure

2. Run ROSDiscover to statically recover the system.

.. code::

  (docker)$ docker/run.sh recover recovery autorally
  (native)$ pipenv run scripts/recover-system.py recovery autorally

  INFO: reconstructing architecture for image [rosdiscover-experiments/autorally:c2692f2]
  ...
  INFO: applying remapping from [/camera/left/camera_info] to [/left_camera/camera_info]
  INFO: applying remapping from [/camera/right/camera_info] to [/right_camera/camera_info]
  INFO: statically recovered system architecture for image [rosdiscover-experiments/autorally:c2692f2]

This will process the launch files supplied in the `experiment.yml` and produce the architecture in `experiments/recovery/subjects/autorally/recovered.architecture.yml`. The first time this is run it may take some time because it needs to statically analyze the source for the nodes mentioned in the launch files, but thereafter those results are cached and the analysis will run more quickly.

3. Check and compare the architectures of the observed and recovered systems. This involves three steps.
  a. Produce and check the architecture of the observed system

.. code::

  (docker)$ docker/run.sh check observed recovery autorally
  (native)$ pipenv run scripts/check-architecture.py observed experiments/recovery/subjects/autorally/experiment.yml

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

  (docker)$ docker/run.sh check recovered recovery autorally
  (native)$ pipenv run scripts/check-architecture.py recovered experiments/recovery/subjects/autorally/experiment.yml

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

  (docker)$ docker/run.sh compare autorally
  (native)$ pipenv run scripts/compare-recovered-observed.py autorally

The comparison output is placed in `experiments/recovery/subjects/autorally/compare.observed-recovered.log`. The analyzed results used in the paper are in `experiments/recovery/subjects/autorally/observed.recovered.compare.csv`.


If you look at the file `experiments/recovery/subjects/autorally/observed.recovered.compare.csv` (**TODO: Add link to result in repo**), it is divided into five sections. 

1. Observed architecture summary. This summarizes the observed architceture. It is a summarization of `experiments/recovery/subjects/autorally/observed.architecture.acme`
2. Recovered architecture summary. This summarizes the recovered architecture. It is a summarization of `experiments/recovery/subjects/autorally/recovered.architecture.acme` 
3. Provenance information. This summarizes the component models used in recovery that were handwritten and recovered.
4. Side-by-side comparison: This gives a side by side comparison of the details of the architecture, giving topics etc that were observed for a node, those that were recovered. Upper case elements are those that appear in both the observed and recovered architectures, those in lower case only appear in one.
5. Differences: A summary of the statistics for over-approximation/under-approximation for the whole system (not that in `observed.recovered.compare.csv` we divide these numbers into handwritten and recovered, and only use the recovered metrics in the paper.

Run configuration mismatch bug detection for RQ3
------------------------------------------------

To run configuration mismatch bugs for RQ3 involves building another set of Docker images that build the system
representing the system at the time the misconfiguration was extant and the time at which it was fixd. Like the other
RQs, we use use the same scripts for building these images. We will use the example of the `autorally-01` bug which
is an error that was introduced into the `autorally_core/launch/stateEstimator.launch` file that incorrectly remapped
a topic. The format of the experiment definition for detection replication is different to the other experiment
defintions, containing information on how to build the buggy and fixed docker images, the errors that are expected to
be found, and definition of a reproducer node that guarantees use of the broken connector. We provide the pre-built
images. See `INSTALL <INSTALL.rst>`_.

To reproduce the results for RQ3, we have provided a script that automates the process above for the detection
experiment. The script:

1. Recovers the architectures of both the buggy and fixed versions, as described in the corresponding `experiment.yml`.
2. Applies the architectural rule checking to both architectures and outputs any found errors
3. Summarizes the results. The results first print any architecture errors found in the buggy version of the system,
followed by
any architecture errors in the fixed version. If the buggy version contains errors, but the fixed version prints out
**NO RELEVANT
RESULTS** this means we have succcessfully detected the bug.

To run RQ3 reproduction on all the systems we detected:

.. code::

  (docker)$ docker/run.sh rq3
  (native)$ pipenv run rq3

This will run RQ3 on all the images that we were successful in detecting: autorally-01, autorally-03, autorally-04,
autoware-01, autoware-11 husky-02 husky-04 husky-06. To run on an individual example:

.. code::

  (docker)$ docker/run.sh rq3 autorally-01
  (native)$ pipen run rq3 autorally-01

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

  [recovered,obeserved].architecture.[yml,acme]   - recovered and observed architectures
  compare.observed-recovered.txt                  - a human readable summary of the comparison
  observed.recovered.[compare,errors].csv         - a CSV version of the comparison results,
                                                    with errors detected
  recovery.rosdiscover.yml                        - a script generated config file passed to rosdiscover
  recovered-models.csv                            - a list of models recovered for RQ1 and the accuracy
                                                    metrics

Processed Results and Data Analysis
-----------------------------------

In order to produce the results presented in the paper, we combined the results into various files that can
be analyzed by a Jupyter notebook. These can be reproduced.

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

To reproduce the comparison files, you can run:

.. code::

  (native)$ pipenv scripts/gather-rq2-results.py
  (container)$ docker/run.sh gather-rq2

This pulls information out of the `compare.observed.recovered.csv` files into the Comparison csvs mentioned above.
They can the be analyzed like mentioned below.

The data collected for the experiments of RQ3 is in: results/data/RosTopicBugs - RQ3 - Results Table.csv

The Jupyer Notebook in results/DataAnalysis.ipynb uses these results to aggregate them to produce the numbers in the paper. To run this analysis, you can run the following command locally via pipenv: (TODO: add Docker-based instructions.)

.. code::

   (native)$ pipenv run jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser results/DataAnalysis.ipynb
   (container)$ docker/run.sh jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser results/DataAnalysis.ipynb

This will start the Jupyter notebook, which can be accessed by opening a browser to the address: 192.168.0.1:8080"


Results Format
--------------
The Jupter notebook writes the results into these files:

- results/RQ1.csv (which includes the nodel-level accuracy results shown in Table III in the paper)
- results/RQ1_unreachable.csv (which includes the nodel-level static analysis results of unreachable statements and functions)
- results/RQ2.csv (which includes the system-level static analysis accurary results shown in Table IV in the paper)
- results/RQ2_architectural_element.csv (which includes the system-level static analysis accurary results per architectural element shown in Table V in the paper)
- results/RQ2_handwritten.csv (which includes the system-level accurary of handwritten models discusssed in Section IV.B. RQ2 – System Architecture Recovery - Results of the paper)
- results/RQ2_handwritten_architectural_element.csv (which includes the system-level accurary of handwritten models discusssed in Section IV.B. RQ2 – System Architecture Recovery - Results of the paper per architectural element)
- results/RQ3.csv (which includes the data shown in Table VI of the paper)

Furthermore, results/modelSizes.csv lists the lines of code for each handwritten model of the corresponding file in deps/rosdiscover/src/rosdiscover/models.
