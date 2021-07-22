all: pre-bug bug bug-fix

pre-bug:
	/bin/bash -c 'cd /src_pre_bug/repo/ros; ./catkin_make_release' 
bug:
	/bin/bash -c 'cd /src_bug/repo/ros; ./catkin_make_release' 
bug-fix:
	/bin/bash -c 'cd /src_bug_fix/repo/ros; cp /src_pre_bug/repo/ros/catkin_make_release .; ./catkin_make_release'
