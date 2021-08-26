#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


class NodeSources(t.TypedDict):
    package: str
    node: str
    entrypoint: t.Optional[str]
    sources: t.Collection[str]
    type: t.Optional[t.Union[t.Literal["nodelet"], t.Literal["node"]]]
    restrict_analysis_to_paths: t.Collection[str]


class ExperimentConfig(t.TypedDict):
    directory: str
    subject: str
    version: str
    distro: str
    image: str
    sources: t.Sequence[str]
    node_sources: t.Collection[NodeSources]


class RecoveryConfig(t.TypedDict):
    image: str
    sources: t.Sequence[str]
    # FIXME we need a set of launches to get the recovery command to work right now, which is a bit of a hack
    launches: t.Sequence[str]


def find_node_sources(
    experiment_config: ExperimentConfig,
    package: str,
    node: str,
) -> NodeSources:
    for node_sources in experiment_config["node_sources"]:
        if node_sources["package"] == package and node_sources["node"] == node:
            return node_sources
    raise ValueError(f"failed to find sources for node [{node}] in package [{package}]")


def recover_all(experiment_config: ExperimentConfig) -> None:
    logger.info("recovering all node models for system")
    for node_sources in experiment_config["node_sources"]:
        recover_node_from_sources(experiment_config, node_sources)
    logger.info("recovered all node models for system")


def recover_node(
    experiment_config: ExperimentConfig,
    package: str,
    node: str,
) -> None:
    node_sources = find_node_sources(experiment_config, package, node)
    return recover_node_from_sources(experiment_config, node_sources)


def recover_node_from_sources(
    experiment_config: ExperimentConfig,
    node_sources: NodeSources,
) -> None:
    entrypoint = node_sources.get("entrypoint", "main")
    package = node_sources["package"]
    node = node_sources["node"]
    sources = node_sources["sources"]
    restrict_to_paths = node_sources["restrict_analysis_to_paths"]
    logger.info(f"statically recovering model for node [{node}] in package [{package}]")

    # ensure that a models output directory exists for this system
    experiment_directory = experiment_config["directory"]
    models_directory = os.path.join(experiment_directory, "models")
    logs_directory = os.path.join(experiment_directory, "logs")
    os.makedirs(models_directory, exist_ok=True)
    os.makedirs(logs_directory, exist_ok=True)
    model_filename = os.path.join(models_directory, f"{package}__{node}.json")
    log_filename = os.path.join(logs_directory, f"{package}__{node}.log")

    recovery_config: t.Dict[str, t.Any] = {
        "image": experiment_config["image"],
        "sources": list(experiment_config["sources"]),
        "launches": list(experiment_config["launches"]),
    }


    try:
        recovery_config_filename: str = tempfile.mkstemp(suffix=".rosdiscover.yml")[1]
        with open(recovery_config_filename, "w") as fh:
            yaml.dump(recovery_config, fh, default_flow_style=False)

        args = [
            "recover",
            "--save-to",
            model_filename,
            recovery_config_filename,
            package,
            node,
            entrypoint,
        ]
        for restrict_to in restrict_to_paths:
            args += ["--restrict-to", restrict_to]
        args += sources

        file_logger = logger.add(log_filename, level="DEBUG")
        logger.debug(f"calling rosdiscover: {args}")
        try:
            rosdiscover.cli.main(args)
        except Exception:
            logger.exception(f"failed to statically recover model for node [{node}] in package [{package}]")
        finally:
            logger.remove(file_logger)

        logger.info(f"statically recovered model for node [{node}] in package [{package}]")

    finally:
        os.remove(recovery_config_filename)


def load_experiment_config(filename: str) -> ExperimentConfig:
    abs_filename = os.path.abspath(filename)
    experiment_directory = os.path.dirname(abs_filename)
    with open(filename, "r") as fh:
        config = yaml.safe_load(fh)
        config["directory"] = experiment_directory
        return config


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

    parser = argparse.ArgumentParser("statically recovers node models")
    parser.add_argument(
        "configuration",
        help="the path to the configuration file for the system",
    )
    parser.add_argument(
        "--package",
        default=None,
        required=False,
        help="the name of the package containing the node whose model should be recovered",
    )
    parser.add_argument(
        "--node",
        default=None,
        required=False,
        help="the name of the node whose model should be recovered",
    )
    args = parser.parse_args()

    if args.node and not args.package:
        error(f"expected package name to be specified for node [{args.node}]")

    if args.package and not args.node:
        error(f"expected node name to be specified along with package [{args.package}]")

    experiment_filename: str = args.configuration
    if not os.path.exists(experiment_filename):
        error(f"configuration file not found: {experiment_filename}")

    # load experiment config
    config = load_experiment_config(experiment_filename)

    # determine if we should recover all models or just one
    should_recover_all = not args.node
    if should_recover_all:
        recover_all(config)
    else:
        recover_node(config, args.package, args.node)


if __name__ == "__main__":
    main()
