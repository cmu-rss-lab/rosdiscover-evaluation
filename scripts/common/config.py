# -*- coding: utf-8 -*-
__all__ = (
    "DetectionExperimentConfig",
    "ExperimentConfig",
    "NodeSources",
    "ROSDiscoverConfig",
    "RecoveryExperimentConfig",
    "RepoVersion",
    "SystemVersion",
    "find_configs",
    "load_config",
)

import contextlib
import os
import tempfile
import typing as t

from loguru import logger
import yaml


class NodeSources(t.TypedDict):
    package: str
    node: str
    entrypoint: t.Optional[str]
    sources: t.Collection[str]
    type: t.Optional[t.Union[t.Literal["nodelet"], t.Literal["node"]]]
    restrict_analysis_to_paths: t.Collection[str]


class ROSDiscoverConfig(t.TypedDict):
    image: str
    subject: str
    sources: t.Sequence[str]
    launches: t.Sequence[str]
    node_sources: t.Optional[t.Collection[NodeSources]]
    run_script: t.Optional[str]

    @classmethod
    @contextlib.contextmanager
    def create_temporary(cls, config: "ROSDiscoverConfig") -> t.Iterator[str]:
        """Creates a scope-managed temporary file on disk from a given config."""
        try:
            filename: str = tempfile.mkstemp(suffix=".rosdiscover.yml")[1]
            with open(filename, "w") as fh:
                yaml.dump(config, fh, default_flow_style=False)
            with open(filename, "r") as fh:
                logger.debug(f"generated temporary ROSDiscover config file [{filename}]:\n{fh.read()}")

            yield filename
        finally:
            if filename:
                os.remove(filename)


class RepoVersion(t.TypedDict):
    name: str
    url: str
    version: str


class SystemVersion(t.TypedDict):
    image: str
    build_command: str
    repositories: t.Collection[RepoVersion]


class ExperimentConfig(t.TypedDict):
    type: t.Union[t.Literal["detection"], t.Literal["recovery"]]
    directory: str
    subject: str
    distro: str
    apt_packages: t.Optional[t.Collection[str]]
    missing_ros_packages: t.Optional[t.Collection[str]]
    sources: t.Sequence[str]
    environment: t.Mapping[str, str]
    launches: t.Sequence[str]
    node_sources: t.Collection[NodeSources]


class RecoveryExperimentConfig(ExperimentConfig):
    image: str
    build_command: str
    version: str
    repositories: t.Collection[RepoVersion]
    config_with_node_sources_filename: str


class DetectionExperimentConfig(ExperimentConfig):
    buggy: SystemVersion
    fixed: SystemVersion


def load_config(filename: str) -> ExperimentConfig:
    abs_filename = os.path.abspath(filename)
    experiment_directory = os.path.dirname(abs_filename)

    if not os.path.exists(filename):
        raise ValueError(f"experiment file not found: {filename}")

    with open(filename) as fh:
        config = yaml.safe_load(fh)

    config["filename"] = abs_filename
    config["directory"] = experiment_directory
    config["node_sources"] = config.get("node_sources") or []
    config["environment"] = config.get("environment") or {}

    if config["type"] == "recovery":
        config["config_with_node_sources_filename"] = os.path.join(
            config["directory"],
            "rosdiscover-config-with-sources.yml",
        )

    return config


def find_configs() -> t.Iterator[str]:
    """Returns an iterator over the absolute paths of all of the experiment config
    files in this replication package."""
    dir_scripts = os.path.dirname(os.path.dirname(__file__))
    dir_replication_package = os.path.dirname(dir_scripts)
    for root, _dirs, files in os.walk(dir_replication_package):
        for filename in files:
            if filename == "experiment.yml":
                yield os.path.join(root, filename)
