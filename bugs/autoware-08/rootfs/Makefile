all: pre-bug bug bug-fix

pre-bug:
	/bin/bash -c 'cd /pre_bug/src/repo/ros; ./catkin_make_release "-DCMAKE_EXPORT_COMPILE_COMMANDS=1 -D_GLIBCXX_USE_CXX11_ABI=0"' 
bug:
	/bin/bash -c 'cd /bug/src/repo/ros; ./catkin_make_release "-DCMAKE_EXPORT_COMPILE_COMMANDS=1 -D_GLIBCXX_USE_CXX11_ABI=0"' 
bug-fix:
	/bin/bash -c 'cd /bug_fix/src/repo/ros; ./catkin_make_release "-DCMAKE_EXPORT_COMPILE_COMMANDS=1 -D_GLIBCXX_USE_CXX11_ABI=0"'

.PHONY: pre-bug bug bug-fix
