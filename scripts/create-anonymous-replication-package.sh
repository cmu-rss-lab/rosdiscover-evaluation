#!/bin/bash
#
# This script transforms this repository into an anonymized .tar.gz replication package
# intended for the technical track submission. The anonymous replication package is NOT
# intended for artifact evaluation; the standard replication package will be provided
# instead.
#
set -eu

HERE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
REPO_ROOT="${HERE_DIR}/.."
OUTPUT_FILENAME="${REPO_ROOT}/anonymous-replication-package.zip"

zip -r "${OUTPUT_FILENAME}" \
  deps \
  docker \
  experiments \
  rootfs \
  scripts \
  .dockerignore \
  Pipfile \
  Pipfile.lock \
  README.rst
  Dockerfile.autoware
