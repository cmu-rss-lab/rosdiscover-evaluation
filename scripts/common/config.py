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
import pathlib
import re
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
    def create(cls, config: "ROSDiscoverConfig", filename: str) -> None:
        with open(filename, "w") as fh:
            yaml.dump(config, fh, default_flow_style=False)
        with open(filename, "r") as fh:
            logger.debug(f"generated ROSDiscover config file [{filename}]:\n{fh.read()}")


    @classmethod
    @contextlib.contextmanager
    def create_temporary(cls, config: "ROSDiscoverConfig") -> t.Iterator[str]:
        """Creates a scope-managed temporary file on disk from a given config."""
        try:
            filename: str = tempfile.mkstemp(suffix=".rosdiscover.yml")[1]
            cls.create(config, filename)
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
    errors: t.Sequence[str]


def load_config(experiment_kind: str, subject: str, experiment_filename: str, results_dir: str) -> ExperimentConfig:
    config_file = configuration_to_experiment_file(experiment_kind, subject, experiment_filename)
    if not pathlib.Path(config_file).exists():
        raise ValueError(f"Could not find experiment configuration file '{config_file}")
    file_path = pathlib.Path(config_file)
    abs_filepath = file_path.absolute()
    experiment_directory = abs_filepath.parent
    results_directory = configuration_to_results_directory(experiment_kind, subject, results_dir)

    if not os.path.exists(config_file):
        raise ValueError(f"experiment file not found: {config_file}")

    with open(config_file) as fh:
        config = yaml.safe_load(fh)

    config["filename"] = str(abs_filepath)
    config["directory"] = experiment_directory
    config["results_directory"] = results_directory
    config["node_sources"] = config.get("node_sources") or []
    config["environment"] = config.get("environment") or {}
    config["reproducer"] = config.get("reproducer") or {}

    if config["type"] == "recovery":
        config["config_with_node_sources_filename"] = os.path.join(
            config["directory"],
            "rosdiscover-config-with-sources.yml",
        )
    if config["type"] == "detection":
        config["errors"] = config.get("errors") or []

    return config


def find_configs() -> t.Iterator[str]:
    """Returns an iterator over the absolute paths of all of the experiment config
    files in this replication package."""
    dir_scripts = os.path.dirname(os.path.dirname(__file__))
    dir_replication_package = os.path.dirname(dir_scripts)
    for root, _dirs, files in os.walk(dir_replication_package):
        for filename in files:
            if re.match(r"experiment.*\.yml", filename):
                yield os.path.join(root, filename)


def configuration_to_results_directory(experiment_kind: str, subject: str, results_dir: str) -> str:
    if pathlib.Path(results_dir).is_absolute():
        return results_dir
    return str(pathlib.Path(__file__).parent.parent.parent / results_dir / experiment_kind / 'subjects' / subject)


def configuration_to_experiment_file(experiment: str, system: str, experiment_file: str) -> str:
    subject_dir = pathlib.Path(__file__).parent.parent.parent / "experiment" / experiment / "subjects"
    experiment_path = subject_dir / system / experiment_file

    if not experiment_path.is_file():
        valid_experiments = "\n  ".join(os.listdir(subject_dir))
        raise ValueError(f"'{experiment}':'{system}' combination not found. Couldn't find file {experiment_path}. "
                         f"Valid systems are:\n  "
                         f"{valid_experiments}")

    return str(experiment_path)
