#!/bin/bash
set -eu

HERE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ROOT_DIR="${HERE_DIR}/.."
ROSDISCOVER_CXX_DIR="${ROOT_DIR}/deps/rosdiscover-cxx-recover"

# TODO ensure that the user has Docker installed

# TODO ensure that the user has make installed

# TODO ensure that the user has jq installed

# TODO ensure that the version of Docker is recent enough; if not, produce a warning

echo "installing rosdiscover experiment runner image..."
docker build -f "${HERE_DIR}/Dockerfile.runner" -t rosqual/icsa22-evaluation:runner "${ROOT_DIR}"

echo "installing rosdiscover C++ recovery volume..."
make -C "${ROSDISCOVER_CXX_DIR}/docker"
