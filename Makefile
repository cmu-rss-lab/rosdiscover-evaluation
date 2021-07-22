all: autoware

autoware: autoware-01 autoware-02 autoware-03 autoware-04 autoware-05

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
