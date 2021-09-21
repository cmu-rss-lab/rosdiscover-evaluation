#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to statically recover run-time architectures for entire ROS systems."""
import argparse
import os
import sys
import tempfile
import typing as t

from loguru import logger
logger.remove()

import rosdiscover
import rosdiscover.cli

import yaml

from common.config import (
    DetectionExperimentConfig,
    ExperimentConfig,
    NodeSources,
    RecoveryExperimentConfig,
    ROSDiscoverConfig,
    load_config
)

def main() -> None:
    # remove all existing loggers
    stderr_logger = logger.add(
        sys.stderr,
        colorize=True,
        format="<bold><level>{level}:</level></bold> {message}",
        level="INFO",
    )

    parser = argparse.ArgumentParser("statically recovers ROS system architectures")
    parser.add_argument(
        "configuration",
        help="the path to the configuration file for this experiment",
    )
    parser.add_argument(
        "version",
        help="buggy or fixed",
    )
    args = parser.parse_args()

    experiment_filename: str = args.configuration
    version: str = args.version
    if not os.path.exists(experiment_filename):
        error(f"configuration file not found: {experiment_filename}")

    if not version in ["buggy", "fixed"]:
        error(f"version needs to be buggy or fixed")
    config = load_config(experiment_filename)
    image = config[version]["image"]
    os.system(f'docker run -it --rm {image}')


if __name__ == "__main__":
    main()
