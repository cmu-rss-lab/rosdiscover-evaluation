#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import typing as t

from loguru import logger

from common import generate_and_check_acme
from common.config import (
    DetectionExperimentConfig,
    ExperimentConfig,
    RecoveryExperimentConfig,
    load_config,
)


def check(config: ExperimentConfig) -> None:
    ({
        "detection": _check_for_detection_experiment,
        "recovery": _check_for_recovery_experiment,
    })[config["type"]](config)


def _check_for_detection_experiment(config: DetectionExperimentConfig) -> None:
    error(f"{config['type']} not yet supported for detection experiment")


def _check_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    config_directory = config["directory"]
    log_directory = os.path.join(config_directory, "logs")
    output_filename = os.path.join(config_directory, "observed.architecture.yml")

    acme_filename = os.path.join(config_directory, "observed.archiecture.acme")
    acme_log_filename = os.path.join(log_directory, "acme-and-check-observed.log")
    generate_and_check_acme(
        image=config["image"],
        input_filename=output_filename,
        output_filename=acme_filename,
        log_filename=acme_log_filename,
    )


def error(message: str) -> t.NoReturn:
    print(f"ERROR: {message}")
    sys.exit(1)


def main():
    # remove all existing loggers
    stderr_logger = logger.add(
        sys.stderr,
        colorize=True,
        format="<bold><level>{level}:</level></bold> {message}",
        level="INFO",
    )
    parser = argparse.ArgumentParser("dynamically recovers ROS system architectures")
    parser.add_argument(
        "configuration",
        help="the path to the configuration file for this experiment",
    )
    args = parser.parse_args()

    experiment_filename: str = args.configuration
    if not os.path.exists(experiment_filename):
        error(f"configuration file not found: {experiment_filename}")
    config = load_config(experiment_filename)

    check(config)


if __name__ == "__main__":
    main()
