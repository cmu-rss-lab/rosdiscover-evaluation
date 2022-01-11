#!/bin/bash
set -eu

HERE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ROOT_DIR="${HERE_DIR}/.."

# TODO ensure that the user has Docker installed

# TODO ensure that the version of Docker is recent enough; if not, produce a warning

docker build -f "${HERE_DIR}/Dockerfile.runner" -t rosqual/icsa22-evaluation:runner "${ROOT_DIR}"
