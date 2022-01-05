#!/bin/bash
set -eu

HERE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

DOCKERFILE_AUTOWARE="${HERE_DIR}/Dockerfile.autoware"

while true; do
  read -p "Would you like to build the image for the Autoware recovery experiment? " yn
  case $yn in
    [Yy]* ) docker build -f "${DOCKERFILE_AUTOWARE}" -t rosdiscover-experiments/autoware:static "${HERE_DIR}"; break;;
    [Nn]* ) exit;;
    * ) echo "> Please answer yes or no: ";;
  esac
done
