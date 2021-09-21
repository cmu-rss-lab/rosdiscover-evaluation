#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import contextlib
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
    NodeSources,
    RecoveryExperimentConfig,
    load_config
)


class RecoveryConfig(t.TypedDict):
    image: str
    sources: t.Sequence[str]
    # FIXME we need a set of launches to get the recovery command to work right now, which is a bit of a hack
    launches: t.Sequence[str]


@contextlib.contextmanager
def generate_temporary_recovery_config(
    experiment_config: RecoveryExperimentConfig,
) -> t.Iterator[str]:
    """Creates a temporary ROSDiscover config file for a given recovery experiment."""
    recovery_config: t.Dict[str, t.Any] = {
        "image": experiment_config["image"],
        "sources": list(experiment_config["sources"]),
        "launches": list(experiment_config["launches"]),
    }

    try:
        recovery_config_filename: str = tempfile.mkstemp(suffix=".rosdiscover.yml")[1]
        with open(recovery_config_filename, "w") as fh:
            yaml.dump(recovery_config, fh, default_flow_style=False)

        yield recovery_config_filename

    finally:
        os.remove(recovery_config_filename)


def generate_node_sources(
    experiment_config: RecoveryExperimentConfig,
) -> None:
    """Generates a config file with node/nodelet sources information for a given experiment."""
    config_with_node_sources_filename = experiment_config["config_with_node_sources_filename"]
    with generate_temporary_recovery_config(experiment_config) as recovery_config_filename:
        args = [
            "sources",
            "--save-to",
            config_with_node_sources_filename,
            recovery_config_filename,
        ]

        logger.debug(f"calling rosdiscover: {args}")
        try:
            rosdiscover.cli.main(args)
        except Exception:
            logger.exception("failure occurred when recovering node sources")
            error(f"failed to obtain node sources for experiment [{experiment_config['filename']}]")


def obtain_node_sources(
    experiment_config: RecoveryExperimentConfig,
) -> t.Mapping[t.Tuple[str, str], NodeSources]:
    config_with_node_sources_filename = experiment_config["config_with_node_sources_filename"]

    if not os.path.exists(config_with_node_sources_filename):
        generate_node_sources(experiment_config)

    with open(config_with_node_sources_filename, "r") as fh:
        dict_ = yaml.safe_load(fh)

    node_sources: t.Collection[NodeSources] = dict_["node_sources"]
    package_node_to_sources: t.Mapping[t.Tuple[str, str], NodeSources] = {
        (ns["package"], ns["node"]): ns for ns in node_sources
    }
    return package_node_to_sources


def recover_all(
    experiment_config: RecoveryExperimentConfig,
) -> None:
    logger.info("recovering all node models for system")
    package_node_to_sources = obtain_node_sources(experiment_config)
    for node_sources in package_node_to_sources.values():
        recover_node_from_sources(experiment_config, node_sources)
    logger.info("recovered all node models for system")


def recover_single_node(
    experiment_config: RecoveryExperimentConfig,
    package: str,
    node: str,
) -> None:
    package_node_to_sources = obtain_node_sources(experiment_config)
    try:
        node_sources = package_node_to_sources[(package, node)]
    except KeyError:
        error(f"failed to find sources for node [{node}] in package [{package}]")
    return recover_node_from_sources(experiment_config, node_sources)


def recover_node_from_sources(
    experiment_config: RecoveryExperimentConfig,
    node_sources: NodeSources,
) -> None:
    entrypoint = node_sources.get("entrypoint", "main")
    package = node_sources["package"]
    node = node_sources["node"]
    sources = node_sources["sources"]
    restrict_to_paths = node_sources["restrict-analysis-to-paths"]
    logger.info(f"statically recovering model for node [{node}] in package [{package}]")

    # ensure that a models output directory exists for this system
    experiment_directory = experiment_config["directory"]
    models_directory = os.path.join(experiment_directory, "models")
    logs_directory = os.path.join(experiment_directory, "logs")
    os.makedirs(models_directory, exist_ok=True)
    os.makedirs(logs_directory, exist_ok=True)
    model_filename = os.path.join(models_directory, f"{package}__{node}.json")
    log_filename = os.path.join(logs_directory, f"{package}__{node}.log")

    with generate_temporary_recovery_config(experiment_config) as recovery_config_filename:
        args = [
            "recover",
            "--save-to",
            model_filename,
            "--entrypoint",
            entrypoint,
        ]
        for restrict_to in restrict_to_paths:
            args += ["--restrict-to", restrict_to]

        args += [
            recovery_config_filename,
            package,
            node,
        ]
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


def error(message: str) -> t.NoReturn:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enables verbose logging for debugging purposes",
    )
    args = parser.parse_args()

    # enable logging
    debug_level = "DEBUG" if args.debug else "INFO"
    stderr_logger = logger.add(
        sys.stderr,
        colorize=True,
        format="<bold><level>{level}:</level></bold> {message}",
        level=debug_level,
    )

    if args.node and not args.package:
        error(f"expected package name to be specified for node [{args.node}]")

    if args.package and not args.node:
        error(f"expected node name to be specified along with package [{args.package}]")

    experiment_filename: str = args.configuration
    if not os.path.exists(experiment_filename):
        error(f"configuration file not found: {experiment_filename}")

    # load experiment config
    config = load_config(experiment_filename)
    if config["type"] != "recovery":
        error(f"this script can only be run on recovery experiments")

    # determine if we should recover all models or just one
    should_recover_all = not args.node
    if should_recover_all:
        recover_all(config)
    else:
        recover_node(config, args.package, args.node)


if __name__ == "__main__":
    main()
