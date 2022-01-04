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
if [[ $DOCKER_HOST == unix:* ]]; then
  docker_host="${DOCKER_HOST:7}"
else
  docker_host="${DOCKER_HOST}"
fi
docker run --user $(id -u) -v "$docker_host":/var/run/docker.sock \
	-v "$current_dir/experiments":/opt/rosdiscover/evaluation/experiments \
 	-v "$current_dir/cache/":/root/.roswire rosdiscover/evaluation "$@"
