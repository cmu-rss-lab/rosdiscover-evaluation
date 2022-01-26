#!/bin/bash
set -eu
PROG=$0

if  [[ $# -eq 0 ]]; then
  targets="autorally-01 autorally-03 autorally-04 autoware-01 autoware-11 husky-02 husky-04 husky-06"
else
  targets=$@
fi

if [ ! -d "scripts" ]; then
  echo "'$PROG' needs to be run in the root of the repository."
  exit 1
fi

echo "Reproducing results for RQ3 on these targets: $targets"
echo "Using existing images (i.e., not building them from scratch)."

for system in $targets; do
  echo "Doing recovery of $system ..."
  pipenv run recover detection $system
  if [ ! -e "results/detection/subjects/$system/fixed.architecture.yml"  && \
       ! -e "results/detection/subjects/$system/buggy.architecture.yml" ]; then
    echo "Recovery $system's architecture failed to complete successfully"
    echo "Please check the logs and try again."
    echo "Logs can be found on the console, or in:"
    if [ ! -e "results/detection/subjects/$system/fixed.architecture.yml" ]; then
      echo "  'results/detection/subjects/$system/logs/fixed.system-recovery.log"
    fi
    if [ ! -e "results/detection/subjects/$system/buggy.architecture.yml" ]; then
      echo "  'results/detection/subjects/$system/logs/buggy.system-recovery.log"
    fi
    exit 1
  else
    echo "Successfully recovered buggy and fixed versions"
  fi

  echo "Checking recovered architectures for $system ..."
  pipenv run check detected $system
  if [ ! -e "results/detection/subjects/$system/error-report.csv" ]; then
    echo "Error producing architecture error comparison report."
    echo "Please check the logs and try again."
    echo "Logs can be found on the console, or in:"
    echo "  'results/detection/subjects/$system/logs/acme-and-check-buggy.log'"
    echo "  'results/detection/subjects/$system/logs/acme-and-check-fixed.log'"
  else
    echo "Results produced in 'results/detection/subjects/$system/error-report.csv'"
  fi
done
bold=$(tput bold)
normal=$(tput sgr0)

for system in $targets; do
  echo "${bold}Resuit summary for $system:${normal}"
  echo "==============================================="
  buggy_errors=()
  fixed_errors=()
  while IFS="," read -r rec_system rec_kind rec_topic rec_error; do
    if [[ "$rec_kind" == "buggy" && "$rec_error" != "NO RELEVANT ERROR DETECTED" ]]; then
      buggy_errors+=("$rec_error")
    elif [[ "$rec_kind" == "fixed" && "$rec_error" != "NO RELEVANT ERROR DETECTED" ]]; then
      fixed_errors+=("$rec_error")
    fi
  done < <(tail -n +2 results/detection/subjects/$system/error-report.csv)
  if [ ${#buggy_errors[@]} -ne 0 ]; then
    echo "  The results for the buggy version:"
    for error in "${buggy_errors[@]}"; do
      echo "    $error"
    done
  else
    echo "  No errors were found in the buggy system in the part of the system containing the bug."
  fi
  if [[ ${#fixed_errors[@]} -ne 0  || "${fixed_errors[0]}" != "NO RELEVANT ERROR DETECTED" ]]; then
    echo "  The results for the fixed version:"
    for error in "${fixed_errors[@]}"; do
      echo "    $error"
    done
  else
    echo "  No errors were found in the fixed system."
  fi

done
