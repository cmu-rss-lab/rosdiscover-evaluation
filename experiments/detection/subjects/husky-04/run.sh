docker build -t rosdiscover-experiments/husky:husky-04-buggy -f experiments/detection/subjects/husky-04/Dockerfile-reproduce-buggy experiments/detection/subjects/husky-04/
docker build -t rosdiscover-experiments/husky:husky-04-fixed -f experiments/detection/subjects/husky-04/Dockerfile-reproduce-fixed experiments/detection/subjects/husky-04/
pipenv run scripts/recover-system.py experiments/detection/subjects/husky-04/experiment-reproduced.yml
pipenv run python scripts/check-system.py experiments/detection/subjects/husky-04/experiment-reproduced.yml
