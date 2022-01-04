#!/usr/bin/env bash
HERE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
if [ ! -d "HERE_DIR/.roswire_cache" ]; then
  mkdir $HERE_DIR/.roswire_cache
  chmod 777 $HERE_DIR/.roswire_cache
fi

if [ -z "$DOCKER_HOST" ]; then
  echo "Setting DOCKER_HOST to //var/run/docker.sock - assuming you are using a global docker install"
  DOCKER_HOST="//var/run/docker.sock"
fi
if [[ $DOCKER_HOST == unix:* ]]; then
  docker_host="${DOCKER_HOST:7}"
else
  docker_host="${DOCKER_HOST}"
fi
docker run --user $(id -u) \
  -v "$docker_host":/var/run/docker.sock \
	-v "$HERE_DIR/experiments":/opt/rosdiscover/evaluation/experiments \
 	-v "$HERE_DIR/cache/":/root/.roswire rosdiscover/evaluation "$@"
