#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to build the .rosinstall files for a given experiment."""
import argparse
import os
import typing as t

from loguru import logger

from common.config import (
    DetectionExperimentConfig,
    ExperimentConfig,
    RecoveryExperimentConfig,
    RepoVersion,
)


def obtain_rosinstall_for_repo_versions(
    repos: t.Collection[RepoVersion],
    output_filename: str,
) -> None:
    assert repos
    assert os.path.isabs(output_filename)
    raise NotImplementedError


def obtain_rosinstall_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    output_filename = os.path.join(config["directory"], "pkgs.rosinstall")
    obtain_rosinstall_for_repo_versions(config["repositories"])


def obtain_rosinstall_for_detection_experiment(config: DetectionExperimentConfig) -> None:
    raise NotImplementedError


def obtain_rosinstall_for_experiment(filename: str) -> None:
    config: ExperimentConfig = load_config(filename)
    if config["type"] == "detection":
        obtain_rosinstall_for_detection_experiment(config)
    elif config["type"] == "recovery":
        obtain_rosinstall_for_recovery_experiment(config)
    else:
        raise ValueError(f"unknown experiment type: {config['type']}")


def main(args: t.Optional[t.Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser("Obtains .rosinstall files for experiments")
    parser.add_argument("filename", help="the file for the experiment")
    parsed_args = parser.parse_args(args)

    filename = args.filename
    logger.info(f"obtaining .rosinstall files for experiment: {filename}")
    obtain_rosinstall_for_experiment(filename)
    logger.info(f"obtained .rosinstall files for experiment: {filename}")


if __name__ == "__main__":
    main()
