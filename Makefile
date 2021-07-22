autoware-bugs = autoware-01 autoware-02 autoware-03 autoware-04 autoware-05
all-bugs = $(autoware-bugs)

init:
    bash ./setup.sh

all: autoware

install-only:
    for bug in $(autoware-bugs); do \
        python create_image.py bugs/$$bug none; \
    done

autoware: $(autoware-bugs)
autoware-01:
    python create_image.py bugs/autoware-01 Dockerfile-i
autoware-02:
    python create_image.py bugs/autoware-02 Dockerfile-i
autoware-03:
    python create_image.py bugs/autoware-03 Dockerfile-i
autoware-04:
    python create_image.py bugs/autoware-04 Dockerfile-k_4
autoware-05:
    python create_image.py bugs/autoware-05 Dockerfile-k

ros_tms-01:
    python create_image.py bugs/ros_tms-01 none