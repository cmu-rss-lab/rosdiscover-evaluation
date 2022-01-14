#!/bin/bash
set -eu

HERE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ROOT_DIR="${HERE_DIR}/.."
ROSDISCOVER_CXX_DIR="${ROOT_DIR}/deps/rosdiscover-cxx-recover"

function report_error {
  echo $1
  exit 1
}

which docker &> /dev/null || report_error "failed to find command: docker"
which make &> /dev/null || report_error "failed to find command: make"
which jq &> /dev/null || report_error "failed to find command: jq"

echo "installing rosdiscover experiment runner image..."
docker build -f "${HERE_DIR}/Dockerfile.runner" -t rosqual/icsa22-evaluation:runner "${ROOT_DIR}"

echo "installing rosdiscover C++ recovery volume..."
make -C "${ROSDISCOVER_CXX_DIR}/docker"
