#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to statically recover run-time architectures for entire ROS systems."""
import argparse
import os
import sys
import typing as t

import yaml
from loguru import logger

from common.cli import add_common_options

logger.remove()

import rosdiscover
import rosdiscover.cli

from common.config import (
    configuration_to_experiment_file, ExperimentConfig,
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
    results_directory = config["results_directory"]
    log_directory = os.path.join(results_directory, "logs")

    for version in ("buggy", "fixed"):
        output_filename = os.path.join(results_directory, f"{version}.architecture.yml")
        log_filename = os.path.join(log_directory, f"{version}.system-recovery.log")
        rosdiscover_filename = os.path.join(
            results_directory,
            f"recovery.{version}.rosdiscover.yml",
        )
        recover_system(
            image=config[version]["docker"]["image"],
            sources=config["sources"],
            launches=config["launches"],
            node_sources=config["node_sources"],
            output_filename=output_filename,
            log_filename=log_filename,
            rosdiscover_filename=rosdiscover_filename,
        )

        if config["reproducer"] != {}:
            update_system_with_reproducer(config["reproducer"], output_filename)


def _recover_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    config_directory = config["directory"]
    results_directory = config["results_directory"]
    log_directory = os.path.join(results_directory, "logs")
    output_filename = os.path.join(results_directory, "recovered.architecture.yml")
    log_filename = os.path.join(log_directory, "system-recovery.log")
    rosdiscover_filename = os.path.join(results_directory, "recovery.rosdiscover.yml")
    recover_system(
        image=config["docker"]["image"],
        sources=config["sources"],
        launches=config["launches"],
        node_sources=config["node_sources"],
        output_filename=output_filename,
        log_filename=log_filename,
        rosdiscover_filename=rosdiscover_filename,
    )
    if config["reproducer"] != {}:
        update_system_with_reproducer(config["reproducer"], output_filename)


def recover_system(
    image: str,
    sources: t.Sequence[str],
    launches: t.Sequence[str],  # FIXME
    node_sources: t.Collection[NodeSources],
    output_filename: str,
    log_filename: str,
    rosdiscover_filename: str,
) -> None:
    # ensure that the logs directory exists
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    ROSDiscoverConfig.create({
        "image": image,
        "sources": list(sources),
        "launches": list(launches),
        "node_sources": list(node_sources),
    }, rosdiscover_filename)

    args = ["launch", rosdiscover_filename]
    args += ["--output", output_filename]
    log_file = open(log_filename, 'w')
    file_logger = logger.add(log_file, level="DEBUG")
    logger.debug(f"calling rosdiscover: {args}")
    try:
        rosdiscover.cli.main(args)
    except Exception:
        logger.exception(f"failed to statically recover system architecture for image [{image}]")
    finally:
        log_file.close()
        logger.remove(file_logger)
    logger.info(f"statically recovered system architecture for image [{image}]")


def update_system_with_reproducer(reproducer_info, output_filename):
    with open(output_filename, 'r') as f:
        nodes = yaml.safe_load(f)
    reproducer = {
        "action-clients": [],
        "action-servers": [],
        "filename": "/ros_ws/reproduce.launch",
        "fullname": "/ error_reproducer",
        "kind": "error_reproducer",
        "name": "error_reproducer",
        "namespace": "/",
        "nodelet": False,
        "package": "*",
        "provenance": "handwritten",
        "provides": [],
        "pubs": [],
        "reads": [],
        "subs": [],
        "uses": [],
        "writes": [],
    }
    for pub in reproducer_info.get("pubs", []):
        reproducer["pubs"].append({"format": pub["format"],
                                   "name": pub["name"],
                                   "implicit": False})
    for sub in reproducer_info.get("subs", []):
        reproducer["subs"].append({"format": sub["format"],
                                   "name": sub["name"],
                                   "implicit": False})

    nodes.append(reproducer)
    with open(output_filename, 'w') as f:
        yaml.safe_dump(nodes, f)


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
    parser.add_argument('kind', type=str, choices=['recovery', 'detection'],
                        help='The kind of experiment (recovery or detection')
    parser.add_argument('system', type=str, default="all", help='The system to use')
    add_common_options(parser)
    args = parser.parse_args()

    config = load_config(args.kind, args.system, args.experiment, args.results_dir)
    recover(config)


if __name__ == "__main__":
    main()
