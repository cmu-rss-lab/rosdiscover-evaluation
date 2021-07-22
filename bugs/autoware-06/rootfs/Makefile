all: pre-bug bug bug-fix

pre-bug:
	/bin/bash -c 'cd /pre_bug/src/repo/ros; ./catkin_make_release' 
bug:
	/bin/bash -c 'cd /bug/src/repo/ros; ./catkin_make_release' 
bug-fix:
	/bin/bash -c 'cd /bug_fix/src/repo/ros; ./catkin_make_release'