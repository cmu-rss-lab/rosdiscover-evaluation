#!/usr/bin/env bash
current_dir=$(pwd)

if [ ! -d "$current_dir/roswire_cache" ]; then
  mkdir roswire_cache
  chmod 777 roswire_cache
fi

if [ -z "$DOCKER_HOST" ]; then
  echo "Setting DOCKER_HOST to //var/run/docker.sock - assuming you are using a global docker install"
  DOCKER_HOST="//var/run/docker.sock"
fi

docker run -v $DOCKER_HOST:/var/run/docker.sock -v "$current_dir/experiments":/opt/rosdiscover/evaluation/experiments \
 -v "$current_dir/cache/":/root/.roswire rosdiscover/evaluation "$@"
