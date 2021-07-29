all: pre-bug bug bug-fix

pre-bug:
	/bin/bash -c 'cd /pre_bug/src/repo/ros; ./catkin_make -DCMAKE_EXPORT_COMPILE_COMMANDS=1' 
bug:
	/bin/bash -c 'cd /bug/src/repo/ros; ./catkin_make -DCMAKE_EXPORT_COMPILE_COMMANDS=1' 
bug-fix:
	/bin/bash -c 'cd /bug_fix/src/repo/ros; ./catkin_make -DCMAKE_EXPORT_COMPILE_COMMANDS=1' 

.PHONY: pre-bug bug bug-fix