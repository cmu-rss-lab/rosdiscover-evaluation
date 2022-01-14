#!/bin/bash
set -eu
PROG=$0

if  [[ $# -eq 0 ]]; then
  targets="autorally husky turtlebot"
else
  targets=$@
fi

if [ ! -d "scripts" ]; then
  echo "'$PROG' needs to be run in the root of the repository."
  exit 1
fi

echo "Reproducing results for RQ2 on these targets: $targets"

echo "Using existing images (i.e., not building them from scratch)"

for system in $targets; do

  echo "Doing dynamic observation of $system. This may take a while..."
  pipenv run observe $system
  if [ ! -e "results/recovery/subjects/$system/observed.architecture.yml" ]; then
    echo "Observation of $system's architecture failed to complete successfully."
    echo "Please check the logs and try again."
    echo "Logs can be found on the console, or in:"
    echo "  'results/recovery/subjects/$system/logs/system-observed.log'"
    exit 1
  else
    echo "Observed architecture generated into 'results/recovery/subjects/$system/observed.architecture.yml'"
  fi

  echo "Doing static recovery of $system. This may take a while if it is the first time..."
  pipenv run recover recovery $system
  if [ ! -e "results/recovery/subjects/$system/recovered.architecture.yml" ]; then
    echo "Static recovery of $system's architecture fauled to complete successfully."
    echo "Please check the logs and try again."
    echo "Logs can be found on the console, or in:"
    echo "  'results/recovery/subjects/$system/logs/system-recovered.log'"
    exit 1
  else
    echo "Recovered architecture generated into 'results/recovery/subjects/$system/recovered.architecture.yml'"
  fi

  echo "Checking the observed architecture for $system"
  pipenv run check observed $system
  if [ ! -e "results/recovery/subjects/$system/observed.architecture.acme" ]; then
    echo "Failed to check the observed architecture of $system"
    echo "Please check the logs and try again."
    echo "Logs can be found on the console, or in:"
    echo "  'results/recovery/subjects/$system/acme-and-check-observed.txt'"
    exit 1
  else
    echo "Checking complete."
    echo "  The Acme architecture can be found: results/recovery/subjects/$system/observed.architecture.acme"
    echo "  Errors can be inspected: results/recovery/subjects/$system/acme-and-check-observed.txt"
  fi

  echo "Checking the recovered architecture for $system"
  pipenv run check recovered $system
  if [ ! -e "results/recovery/subjects/$system/recovered.architecture.acme" ]; then
    echo "Failed to check the recovered architecture of $system"
    echo "Please check the logs and try again."
    echo "Logs can be found on the console, or in:"
    echo "  'results/recovery/subjects/$system/acme-and-check-recovered.txt'"
    exit 1
  else
    echo "Checking complete."
    echo "  The Acme architecture can be found: results/recovery/subjects/$system/recovered.architecture.acme"
    echo "  Errors can be inspected: results/recovery/subjects/$system/acme-and-check-recovered.txt"
  fi

  echo "Comparing the observed and recovered architectures of $system"
  pipenv run compare $system
    if [ ! -e "results/recovery/subjects/$system/compare.observed-recovered.txt" ]; then
    echo "Failed to compare the recovered architecture of $system"
    echo "Please check the logs and try again."
    exit 1
  else
    echo "Comparison complete. Results can be inspected: 'results/recovery/subjects/$system/compare.observed-recovered.txt'"
  fi

done

echo "Collating the results"
pipenv run gather-rq2

echo "To analyze the results in Jupyter notebook, please do: "
echo "$ <RUN> run jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser results/DataAnalysis.ipynb"
echo "Where <RUN> is either scripts/run.sh or pipenv run, depending on your setup."
echo "Then, open a browser to 192.168.0.1:8080"
