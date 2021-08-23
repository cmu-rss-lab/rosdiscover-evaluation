all: pre-bug bug bug-fix

pre-bug:
	/bin/bash -c 'cd /pre_bug/; rm -rf src/laser_geometry && catkin build -DCMAKE_EXPORT_COMPILE_COMMANDS=1' 
bug:
	/bin/bash -c 'cd /bug/; rm -rf src/laser_geometry && catkin build -DCMAKE_EXPORT_COMPILE_COMMANDS=1' 
bug-fix:
	/bin/bash -c 'cd /bug_fix/; rm -rf src/laser_geometry && catkin build -DCMAKE_EXPORT_COMPILE_COMMANDS=1'

.PHONY: pre-bug bug bug-fix