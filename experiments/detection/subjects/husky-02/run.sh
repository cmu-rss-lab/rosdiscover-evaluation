docker build -t rosdiscover-experiments/husky:husky-02-buggy -f experiments/detection/subjects/husky-02/Dockerfile-reproduce-buggy experiments/detection/subjects/husky-02/
docker build -t rosdiscover-experiments/husky:husky-02-fixed -f experiments/detection/subjects/husky-02/Dockerfile-reproduce-fixed experiments/detection/subjects/husky-02/
pipenv run scripts/recover-system.py experiments/detection/subjects/husky-02/experiment-reproduced.yml
pipenv run python scripts/check-system.py experiments/detection/subjects/husky-02/experiment-reproduced.yml
