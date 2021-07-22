autoware-bugs = autoware-01 autoware-02 autoware-03 autoware-04 autoware-05
all-bugs = $(autoware-bugs)

all: autoware

autoware: $(autoware-bugs)


install-only:
	for bug in $(autoware-bugs); do \
    	python analysis.py bugs/$$bug none; \
	done
autoware-01:
	python analysis.py bugs/autoware-01 Dockerfile-i
autoware-02:
	python analysis.py bugs/autoware-02 Dockerfile-i
autoware-03:
	python analysis.py bugs/autoware-03 Dockerfile-i
autoware-04:
	python analysis.py bugs/autoware-04 Dockerfile-k_4
autoware-05:
	python analysis.py bugs/autoware-05 Dockerfile-k
