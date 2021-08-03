autoware-bugs = autoware-01 autoware-02 autoware-03 autoware-04 autoware-05 autoware-06 autoware-07 autoware-08 autoware-09 autoware-10
mavros-bugs = mavros-01 mavros-02
all-bugs = $(autoware-bugs) $(mavros-bugs) husky-01 industrial_core-01

init:
	bash ./setup.sh

all: $(all-bugs)

install-only:
	for bug in $(all-bugs); do \
		python create_image.py bugs/$$bug none; \
	done

autoware: $(autoware-bugs)

launch-all:
	for bug in $(all-bugs); do \
		bash run_rosdiscover.sh $$bug; \
	done

%: 
	python create_image.py bugs/$@ Dockerfile

%_nb: 
	python create_image.py bugs/$(subst _nb,,$@) Dockerfile_no_build
