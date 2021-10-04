#!/bin/bash
set -e

# setup the pyenv environment
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

source "/opt/ros/${ROS_DISTRO}/setup.bash"
exec "$@"
