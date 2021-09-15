all: pre-bug bug bug-fix

pre-bug_:
	/bin/bash -c 'cd /pre_bug/; catkin_make -DCMAKE_EXPORT_COMPILE_COMMANDS=1'
pre-bug:
	make pre-bug_ || make pre-bug_ || make pre-bug_ || make pre-bug_ || make pre-bug_ || make pre-bug_
bug_:
	/bin/bash -c 'cd /bug/; catkin_make -DCMAKE_EXPORT_COMPILE_COMMANDS=1'
bug: 
	make bug_ || make bug_ || make bug_ || make bug_ || make bug_ || make bug_
bug-fix_:
	/bin/bash -c 'cd /bug_fix/; catkin_make -DCMAKE_EXPORT_COMPILE_COMMANDS=1'
bug-fix:
	make bug-fix_ || make bug-fix_ || make bug-fix_ || make bug-fix_ || make bug-fix_ || make bug-fix_

.PHONY: pre-bug bug bug-fix
