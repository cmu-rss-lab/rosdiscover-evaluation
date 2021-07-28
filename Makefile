autoware-bugs = autoware-01 autoware-02 autoware-03 autoware-04 autoware-05 autoware-06
all-bugs = $(autoware-bugs) mavros-01

init:
	bash ./setup.sh

all: autoware mavros-01

install-only:
	for bug in $(all-bugs); do \
		python create_image.py bugs/$$bug none; \
	done

autoware: $(autoware-bugs)
autoware-01:
	python create_image.py bugs/$@ Dockerfile
autoware-02:
	python create_image.py bugs/$@ Dockerfile
autoware-03:
	python create_image.py bugs/$@ Dockerfile
autoware-03_d:
	python create_image.py bugs/autoware-03 Dockerfile_6
autoware-04:
	python create_image.py bugs/$@ Dockerfile
autoware-05:
	python create_image.py bugs/$@ Dockerfile_6
autoware-06:
	python create_image.py bugs/$@ Dockerfile_6

autoware-06_d:
	python create_image.py bugs/autoware-06 Dockerfile

ros_tms-01:
	python create_image.py bugs/$@ Dockerfile

industrial_core-01:
	python create_image.py bugs/$@ Dockerfile

mavros-01:
	python create_image.py bugs/$@ Dockerfile


