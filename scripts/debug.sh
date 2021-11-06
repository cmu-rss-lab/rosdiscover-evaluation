#!/bin/bash
IMAGE=rosdiscover-experiments/turtlebot:2.4.2
VOLUME_ROSDISCOVER=rosdiscover-cxx-extract-opt

# approach:
#   rosdiscover-cxx-extract
#   -p
#   shlex.quote(os.path.dirname(compile_commands_path))
#   -output-filename
#   json_model_filename

#  -e PATH=/opt/rosdiscover/bin \
#  -e LIBRARY_PATH=/opt/rosdiscover/lib \
#  -e LD_LIBRARY_PATH=/opt/rosdiscover/lib \


docker run \
  -v "${VOLUME_ROSDISCOVER}:/opt/rosdiscover:ro" \
  --rm \
  -it "${IMAGE}"
