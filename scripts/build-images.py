#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script builds all of the Docker images for a given experiment."""
import os
import typing as t

from common.config import (
    DetectionExperimentConfig,
    RecoveryExperimentConfig,
)


def build_image(
    image: str,
    directory: str,
    distro: str,
    rosinstall_filename: str,
    rootfs: str,
    build_command: str,
    apt_packages: t.Optional[t.Sequence[str]],
) -> None:
    assert os.path.isabs(rootfs)
    assert os.path.exists(rootfs)

    if not apt_packages:
        apt_packages = []

    apt_packages_arg = " ".join(apt_packages)
    raise NotImplementedError


def build_images_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    build(
        image=config["image"],
        directory=config["directory"],
        distro=config["distro"],
        rosinstall_filename="pkgs.rosinstall",
        build_command=config["build_command"],
        apt_packages=config["apt_packages"],
    )


def build_images_for_detection_experiment(config: DetectionExperimentConfig) -> None:
    raise NotImplementedError


def build_images_for_experiment(filename: str) -> None:
    logger.info(f"building images for experiment: {filename}")
    config: ExperimentConfig = load_config(filename)
    if config["type"] == "detection":
        build_images_for_detection_experiment(config)
    elif config["type"] == "recovery":
        build_images_for_recovery_experiment(config)
    else:
        raise ValueError(f"unknown experiment type: {config['type']}")
    logger.info(f"built images for experiment: {filename}")


def main(args: t.Optional[t.Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser("Builds Docker images for experiments")
    parser.add_argument("filename", help="the file for the experiment")
    parsed_args = parser.parse_args(args)
    build_images_for_experiment(args.filename)


if __name__ == "__main__":
    main()
