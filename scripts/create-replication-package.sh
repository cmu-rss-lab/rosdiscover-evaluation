#!/bin/bash
#
# This script transforms this repository into a tar.gz replication package.
#
set -eu

HERE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
REPO_ROOT="${HERE_DIR}/.."
OUTPUT_FILENAME="${REPO_ROOT}/replication-package.zip"

zip -r "${OUTPUT_FILENAME}" \
  architecture-style \
  deps \
  docker \
  experiments \
  rootfs \
  results \
  scripts \
  .dockerignore \
  Pipfile \
  Pipfile.lock \
  LICENSE \
  README.rst \
  README.pdf \
  INSTALL.rst \
  INSTALL.pdf \
  STATUS.rst \
  STATUS.pdf
