# -*- coding: utf-8 -*-
__all__ = (
    "DetectionExperimentConfig",
    "ExperimentConfig",
    "NodeSources",
    "RecoveryExperimentConfig",
    "RepoVersion",
    "SystemVersion",
)

import os
import typing as t

import yaml


class NodeSources(t.TypedDict):
    package: str
    node: str
    entrypoint: t.Optional[str]
    sources: t.Collection[str]
    type: t.Optional[t.Union[t.Literal["nodelet"], t.Literal["node"]]]
    restrict_analysis_to_paths: t.Collection[str]


class RepoVersion(t.TypedDict):
    name: str
    url: str
    release: str


class SystemVersion(t.TypedDict):
    image: str
    build_command: str
    repositories: t.Collection[RepoVersion]


class ExperimentConfig(t.TypedDict):
    type: t.Union[t.Literal["detection"], t.Literal["recovery"]]
    directory: str
    subject: str
    version: str
    distro: str
    apt_packages: t.Optional[t.Collection[str]]
    sources: t.Sequence[str]
    node_sources: t.Collection[NodeSources]


class RecoveryExperimentConfig(ExperimentConfig):
    image: str
    build_command: str
    repositories: t.Collection[RepoVersion]


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
    return config
