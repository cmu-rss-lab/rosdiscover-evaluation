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
