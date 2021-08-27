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

EVALUATION_DIR = os.path.dirname(os.path.dirname(__file__))
RGTM_DIR = os.path.join(EVALUATION_DIR, "rosinstall_generator_time_machine")
RGTM_PATH = os.path.join(RGTM_DIR, "rosinstall_generator_tm.sh")


def obtain_rosinstall_for_repo_versions(
    repos: t.Collection[RepoVersion],
    extra_packages: t.Optional[t.Collection[str]],
    output_filename: str,
) -> None:
    assert repos
    assert os.path.isabs(output_filename)

    if not extra_packages:
        extra_packages = []

    raise NotImplementedError


def obtain_rosinstall_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    extra_packages = config.get("missing_ros_packages", [])
    output_filename = os.path.join(config["directory"], "pkgs.rosinstall")
    obtain_rosinstall_for_repo_versions(
        repos=config["repositories"],
        extra_packages=extra_packages,
        output_filename=output_filename,
    )


def obtain_rosinstall_for_detection_experiment(config: DetectionExperimentConfig) -> None:
    extra_packages = config.get("missing_ros_packages", [])
    bug_rosinstall_filename = os.path.join(config["directory"], "bug.rosinstall")
    fix_rosinstall_filename = os.path.join(config["directory"], "fix.rosinstall")

    obtain_rosinstall_for_repo_versions(
        repos=config["buggy"]["repositories"],
        extra_packages=extra_packages,
        output_filename=bug_rosinstall_file,
    )
    obtain_rosinstall_for_repo_versions(
        repos=config["fixed"]["repositories"],
        extra_packages=extra_packages,
        output_filename=fix_rosinstall_file,
    )


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
