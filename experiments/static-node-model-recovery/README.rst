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
3. We found or created a full-system launch file (or sequence of launch files) for each system (e.g., based on provided examples and tutorials).
   We restrict our attention to system configurations that can be reproduced in simulation (i.e., we ignore hardware-specific configurations).
