ROSDiscover Evaluation: Static Node Model Recovery
==================================================

Methodology
-----------

1. We identified the `N-most popular ROS systems on GitHub <https://github.com/topics/ros?o=desc&s=stars>`_ (measured by number of stars).

  * We looked at 5,118 repositories that have the `ros` topic.
  * Alternatively, we could look at the N-most popular systems in Ivano's list.
  * We ignore repositories that provide standalone components (e.g., navigation, moveit) and libraries (e.g., geometry2) but not full systems.
    (However, most of these components are transitively included by some of the full systems that we studied.)

2. We use the time machine to build a Docker image for the most recent release of that system.
3. We obtained a single, representative **full-system launch configuration** for each system.

  * A full-system launch configuration consists of a sequence of launch files that should be launched to bring up the system in simulation.
  * This is obtained by looking at provided examples, documentation, and tutorials.
  * We restrict our attention to system configurations that can be reproduced in simulation (i.e., we ignore hardware-specific configurations).


Systems
-------

* `Autoware-AI (v1.11.0) <https://github.com/Autoware-AI/autoware.ai/tree/1.11.0>`_
* `AutoRally (c2692f2) <https://github.com/AutoRally/autorally/commit/c2692f2970da6874ad9ddfeea3908adaf05b4b09>`_
* `TurtleBot 3 (v1.2.5) <https://github.com/ROBOTIS-GIT/turtlebot3/releases/tag/1.2.5>`_
* `Champ (91a5b5e) <https://github.com/chvmp/champ/tree/91a5b5e7ee3a35ded0333a39e22a916f075c733d>`_
* `Linorobot (v1.4.0) <https://github.com/linorobot/linorobot/releases/tag/v1.4.0>`_
* `Spot Mini Mini (v2.2.0) <https://github.com/OpenQuadruped/spot_mini_mini/releases/tag/v2.2.0>`_
* `ur5_ROS-Gazebo (2f7b9b0) <https://github.com/lihuang3/ur5_ROS-Gazebo>`_
* `HyphaROS MiniCar (fef61e1) <https://github.com/Hypha-ROS/hypharos_minicar/tree/fef61e1757d3e9715aca6f993af1d9f946208a4e>`_
