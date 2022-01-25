# -*- coding: utf-8 -*-
__all__ = (
    "CustomDockerInstructions",
    "DetectionExperimentConfig",
    "DockerInstructions",
    "ExperimentConfig",
    "NodeSources",
    "ROSDiscoverConfig",
    "RecoveryExperimentConfig",
    "RepoVersion",
    "SystemVersion",
    "TemplatedDockerInstructions",
    "find_configs",
    "load_config",
    "EVALUATION_DIR",
)

import contextlib
import os
import pathlib
import re
import tempfile
import typing as t

from loguru import logger
import yaml

EVALUATION_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_RESULTS_DIR = os.path.join(EVALUATION_DIR, "results")


class DockerInstructions(t.TypedDict):
    type: t.Union[t.Literal["templated"], t.Literal["custom"]]
    image: str


class TemplatedDockerInstructions(DockerInstructions):
    pass


class CustomDockerInstructions(DockerInstructions):
    context: str
    file: str


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
    docker: DockerInstructions
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
    exclude_from_replication_package: bool


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


def load_config(
    experiment_kind: str,
    subject: str,
    experiment_filename: str,
    results_dir: str = DEFAULT_RESULTS_DIR,
) -> ExperimentConfig:
    config_file = configuration_to_experiment_file(experiment_kind, subject, experiment_filename)
    config = load_config_from_file(config_file)
    if results_dir:
        results_dir = configuration_to_results_directory(experiment_kind, subject, results_dir)
        os.makedirs(results_dir, exist_ok=True)
        config["results_directory"] = results_dir
    return config


def load_config_from_file(config_filename: str) -> ExperimentConfig:
    file_path = pathlib.Path(config_filename)
    if not file_path.exists():
        raise ValueError(f"Could not find experiment configuration file '{config_file}")
    abs_filepath = file_path.absolute()
    experiment_directory = abs_filepath.parent

    with open(config_filename) as fh:
        config = yaml.safe_load(fh)

    config["filename"] = str(abs_filepath)
    config["directory"] = experiment_directory
    config["node_sources"] = config.get("node_sources") or []
    config["environment"] = config.get("environment") or {}
    config["reproducer"] = config.get("reproducer") or {}
    config["exclude_from_replication_package"] = config.get("exclude_from_replication_package", False)

    if config["type"] == "recovery":
        config["config_with_node_sources_filename"] = os.path.join(
            config["directory"],
            "rosdiscover-config-with-sources.yml",
        )
    if config["type"] == "detection":
        config["errors"] = config.get("errors") or []

    return config


def find_configs(directory: t.Optional[str] = None) -> t.Iterator[str]:
    """Returns an iterator over the absolute paths of all of the experiment config
    files in this replication package. Optionally, only the set of experiment config
    files under a given directory (relative to the root of the replication package)
    will be yielded.
    """
    dir_scripts = os.path.dirname(os.path.dirname(__file__))
    dir_replication_package = os.path.dirname(dir_scripts)

    if directory:
        directory = os.path.join(dir_replication_package, directory)
    else:
        directory = dir_replication_package

    for root, _dirs, files in os.walk(directory):
        for filename in files:
            if re.match(r"experiment.yml", filename):
                yield os.path.join(root, filename)


def configuration_to_results_directory(experiment_kind: str, subject: str, results_dir: str) -> str:
    results_path = pathlib.Path(EVALUATION_DIR) / results_dir
    if pathlib.Path(results_dir).is_absolute():
        results_path = pathlib.Path(results_dir)
    return str(results_path / experiment_kind / 'subjects' / subject)


def configuration_to_experiment_file(experiment_kind: str, system: str, experiment_file: str) -> str:
    subject_dir = pathlib.Path(EVALUATION_DIR) / "experiments" / experiment_kind / "subjects"
    experiment_path = subject_dir / system / experiment_file

    if not experiment_path.is_file():
        valid_experiments = "\n  ".join(os.listdir(subject_dir))
        raise ValueError(f"'{experiment_kind}':'{system}' combination not found. Couldn't find file {experiment_path}. "
                         f"Valid systems are:\n  "
                         f"{valid_experiments}")

    return str(experiment_path)
