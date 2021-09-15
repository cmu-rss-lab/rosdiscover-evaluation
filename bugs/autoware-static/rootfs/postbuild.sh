#!/bin/bash
set -eu

pushd ~/.autoware
bash my_launch.sh

pushd /code/src/repo/ros
sed -i "2s/^/OPTION_TITLE='--title'\\n/" run
