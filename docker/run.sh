#!/usr/bin/env bash
set -eu

HERE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ROOT_DIR="${HERE_DIR}/.."
DOCKER_IMAGE="rosqual/icsa22-evaluation:runner"
CACHE_DIR="${ROOT_DIR}/cache/roswire"
RESULTS_DIR="${ROOT_DIR}/results"

if [ ! -d "${CACHE_DIR}" ]; then
  mkdir -p "${CACHE_DIR}"
  chmod 777 "${CACHE_DIR}"
fi

if [ ! -d "${RESULTS_DIR}" ]; then
  mkdir -p "${RESULTS_DIR}"
  chmod 777 "${RESULTS_DIR}"
fi

if [[ ! -v DOCKER_HOST ]]; then
  echo "Setting DOCKER_HOST to //var/run/docker.sock - assuming you are using a global docker install"
  DOCKER_HOST="//var/run/docker.sock"
elif [[ -z "$DOCKER_HOST" ]]; then
  echo "Setting DOCKER_HOST to //var/run/docker.sock - assuming you are using a global docker install"
  DOCKER_HOST="//var/run/docker.sock"
fi

if [[ $DOCKER_HOST == unix:* ]]; then
  docker_host="${DOCKER_HOST:7}"
else
  docker_host="${DOCKER_HOST}"
fi

docker run \
  --rm \
  -it \
  --user root \
  -v "${docker_host}":/var/run/docker.sock:ro \
  -v "${ROOT_DIR}/experiments":/opt/rosdiscover/evaluation/experiments \
  -v "${RESULTS_DIR}":/opt/rosdiscover/evaluation/results \
  -v "${CACHE_DIR}":/home/rosqual/.roswire/descriptions \
  -v "${ROOT_DIR}/docker":/opt/rosdiscover/evaluation/docker \
  $DOCKER_IMAGE \
  "$@"
