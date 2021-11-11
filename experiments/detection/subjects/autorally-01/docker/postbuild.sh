#!/bin/bash
set -eu

# fix a fatal typo in a nodelet_xml file
sed -i "s#desription#description#g" /ros_ws/src/autorally/autorally_core/nodelet_plugins.xml
