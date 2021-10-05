#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to statically recover run-time architectures for entire ROS systems."""
import argparse
import os
import sys
import typing as t

from loguru import logger

logger.remove()

import rosdiscover
import rosdiscover.cli

from common import generate_and_check_acme
from common.config import (
    ExperimentConfig,
    NodeSources,
    RecoveryExperimentConfig,
    ROSDiscoverConfig,
    load_config
)


def recover(config: ExperimentConfig) -> None:
    ({
        "detection": _recover_for_detection_experiment,
        "recovery": _recover_for_recovery_experiment,
    })[config["type"]](config)


def _recover_for_detection_experiment(config: RecoveryExperimentConfig) -> None:
    config_directory = config["directory"]
    log_directory = os.path.join(config_directory, "logs")

    for version in ("buggy", "fixed"):
        output_filename = os.path.join(config_directory, f"{version}.architecture.yml")
        log_filename = os.path.join(log_directory, f"{version}.system-recovery.log")
        recover_system(
            image=config[version]["image"],
            sources=config["sources"],
            launches=config["launches"],
            node_sources=config["node_sources"],
            environment=config["environment"],
            output_filename=output_filename,
            log_filename=log_filename,
        )


def _recover_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    config_directory = config["directory"]
    log_directory = os.path.join(config_directory, "logs")
    output_filename = os.path.join(config_directory, "recovered.architecture.yml")
    log_filename = os.path.join(log_directory, "system-recovery.log")
    recover_system(
        image=config["image"],
        sources=config["sources"],
        launches=config["launches"],
        environment=config["environment"],
        node_sources=config["node_sources"],
        output_filename=output_filename,
        log_filename=log_filename,
    )
    acme_filename = os.path.join(config_directory, "recovered.archiecture.acme")
    acme_log_filename = os.path.join(log_directory, "acme-and-check-recovered.log")
    generate_and_check_acme(
        image=config["image"],
        input_filename=output_filename,
        output_filename=acme_filename,
        log_filename=acme_log_filename,
    )

def recover_system(
    image: str,
    sources: t.Sequence[str],
    launches: t.Sequence[str],  # FIXME
    node_sources: NodeSources,
    environment,
    output_filename: str,
    log_filename: str,
) -> None:
    # ensure that the logs directory exists
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    with ROSDiscoverConfig.create_temporary({
        "image": image,
        "sources": list(sources),
        "environment": environment,
        "launches": list(launches),
        "node_sources": list(node_sources),
    }) as config_filename:
        args = ["launch", config_filename]
        args += ["--output", output_filename]
        file_logger = logger.add(log_filename, level="DEBUG")
        logger.debug(f"calling rosdiscover: {args}")
        try:
            rosdiscover.cli.main(args)
        except Exception:
            logger.exception(f"failed to statically recover system architecture for image [{image}]")
        finally:
            logger.remove(file_logger)
        logger.info(f"statically recovered system architecture for image [{image}]")


def error(message: str) -> t.NoReturn:
    print(f"ERROR: {message}")
    sys.exit(1)


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
    args = parser.parse_args()

    experiment_filename: str = args.configuration
    if not os.path.exists(experiment_filename):
        error(f"configuration file not found: {experiment_filename}")

    config = load_config(experiment_filename)
    recover(config)


if __name__ == "__main__":
    main()
