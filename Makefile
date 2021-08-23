autoware-bugs = autoware-01 autoware-02 autoware-03 autoware-04 autoware-05 autoware-06 autoware-07 autoware-08 autoware-09 autoware-10 autoware-11 autoware-12 autoware-13 autoware-14 autoware-static
navigation-bugs = navigation-01 navigation-02
mavros-bugs = mavros-01 mavros-02
husky-bugs = husky-01 husky-02 husky-03 husky-04 husky-05 husky-06 husky-07
autorally-bugs = autorally-01 autorally-02 autorally-03 autorally-04 autorally-05 autorally-06 autorally-07 autorally-08
igvc-bugs = igvc-01 igvc-02 igvc-03
turtlebot-bugs = turtlebot-01 turtlebot-02
all-bugs = $(autoware-bugs) $(mavros-bugs) $(husky-bugs) $(autorally-bugs) $(igvc-bugs) $(turtlebot-bugs) $(navigation-bugs) industrial_core-01 ros_tms-01

init:
	bash ./setup.sh

all: $(all-bugs)

install-only:
	for bug in $(all-bugs); do \
		python create_image.py bugs/$$bug none; \
	done

autoware: $(autoware-bugs)

husky: $(husky-bugs)

autorally: $(autorally-bugs)

launch-all:
	for bug in $(all-bugs); do \
		bash run_rosdiscover.sh $$bug; \
	done

autoware-static: 
	docker build . -t autoware-static --build-arg ROOTFS='./rootfs/' -f Dockerfile-autoware


%: 
	python create_image.py bugs/$@ Dockerfile

%_nb: 
	python create_image.py bugs/$(subst _nb,,$@) Dockerfile_no_build
