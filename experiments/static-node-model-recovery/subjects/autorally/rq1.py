#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import typing as t

from loguru import logger
import rosdiscover

import yaml


class NodeSources(t.TypedDict):
    package: str
    node: str
    entrypoint: t.Optional[str]
    sources: t.Collection[str]
    type: t.Optional[t.Union[t.Literal["nodelet"], t.Literal["node"]]]
    restrict_analysis_to_paths: t.Collection[str]


class ExperimentConfig(t.TypedDict):
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


def recover_node(
    experiment_config: ExperimentConfig,
    package: str,
    node: str,
) -> None:
    recovery_config: t.Dict[str, t.Any] = {
        "image": experiment_config["image"],
        "sources": list(experiment_config["sources"]),
        "launches": list(experiment_config["launches"]),
    }

    node_sources = find_node_sources(experiment_config, package, node)
    entrypoint = node_sources["entrypoint"]
    sources = node_sources["sources"]
    restrict_to_paths = node_sources["restrict_analysis_to_paths"]

    try:
        recovery_config_filename: str = tempfile.mkstemp()[1]
        with open(recovery_config_filename, "w") as fh:
            yaml.dump(recovery_config)

        args = [
            "recover",
            recovery_config_filename,
            package,
            node,
            entrypoint,
        ]
        for restrict_to in restrict_to_paths:
            args += ["--restrict-to", restrict_to]
        args += sources

        rosdiscover.cli.main()

    finally:
        os.remove(recovery_config_filename)


def main() -> None:
    # TODO allow script to be run on a system or a single node
    if not sys.argv[1]:
        print(f"USAGE: {sys.argv[0]} [experiment.yml]")
        sys.exit(1)

    experiment_filename: str = sys.argv[1]
    with open(experiment_filename, "r") as fh:
        config = yaml.safe_load(fh)


if __name__ == "__main__":
    main()
