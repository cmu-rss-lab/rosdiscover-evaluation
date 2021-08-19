#!/bin/bash
set -eu


pushd ~
mkdir .autoware
pushd .autoware
wget https://autoware-ai.s3.us-east-2.amazonaws.com/sample_moriyama_data.tar.gz
tar zxfv sample_moriyama_data.tar.gz

wget https://autoware-ai.s3.us-east-2.amazonaws.com/my_launch.sh

wget https://autoware-ai.s3.us-east-2.amazonaws.com/sample_moriyama_150324.tar.gz
tar zxfv sample_moriyama_150324.tar.gz