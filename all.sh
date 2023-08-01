#!/bin/bash

for sys in autoware husky fetch autorally turtlebot 
    do pipenv run scripts/recover-node-models.py $sys
done