#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script builds all of the Docker images for a given experiment."""
import argparse
import os
import subprocess
import typing as t

from loguru import logger

from common.config import (
    configuration_to_experiment_file, DetectionExperimentConfig,
    RecoveryExperimentConfig,
    load_config,
    find_configs,
)

EVALUATION_DIR = os.path.dirname(os.path.dirname(__file__))
DOCKER_DIR = os.path.join(EVALUATION_DIR, "docker")
DOCKERFILE_PATH = os.path.join(DOCKER_DIR, "Dockerfile")


def build_image(
    image: str,
    directory: str,
    distro: str,
    rosinstall_filename: str,
    build_command: str,
    apt_packages: t.Optional[t.Sequence[str]],
    cuda_version,
) -> None:
    assert os.path.exists(directory)

    if not apt_packages:
        apt_packages = []

    apt_packages_arg = " ".join(apt_packages)
    logger.info(f"apt_packages_arg: {apt_packages_arg}")
    experimentDir = os.path.relpath(directory, EVALUATION_DIR)
    os.makedirs(os.path.join(experimentDir,"docker"), exist_ok=True)
    command_args = ["docker", "build", "-f", DOCKERFILE_PATH]
    command_args += ["--build-arg", "COMMON_ROOTFS=docker/rootfs"]
    command_args += ["--build-arg", f"CUDA_VERSION='{cuda_version}'"]
    command_args += ["--build-arg", f"APT_PACKAGES='{apt_packages_arg}'"]
    command_args += ["--build-arg", f"BUILD_COMMAND='{build_command}'"]
    command_args += ["--build-arg", f"DIRECTORY={experimentDir}"]
    command_args += ["--build-arg", f"ROSINSTALL_FILENAME={rosinstall_filename}"]
    command_args += ["--build-arg", f"DISTRO={distro}"]
    command_args += ["."]
    command_args += ["-t", image]
    command = " ".join(command_args)

    logger.info(f"building image: {command}")
    outcome = subprocess.run(command, cwd=EVALUATION_DIR, shell=True)
    if outcome.returncode == 0:
        logger.info(f"successfully built image: {image}")
    else:
        logger.error(f"failed to build image: {image}")


def build_images_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    build_image(
        image=config["image"],
        directory=config["directory"],
        distro=config["distro"],
        rosinstall_filename="pkgs.rosinstall",
        build_command=config["build_command"],
        apt_packages=config.get("apt_packages", []),
        cuda_version=config.get("cuda_version", 0),
    )


def build_images_for_detection_experiment(config: DetectionExperimentConfig) -> None:
    build_image(
        image=config["buggy"]["image"],
        directory=config["directory"],
        distro=config["distro"],
        rosinstall_filename="bug.rosinstall",
        build_command=config["build_command"],
        apt_packages=config.get("apt_packages", []),
        cuda_version=config.get("cuda_version", 0),
    )
    build_image(
        image=config["fixed"]["image"],
        directory=config["directory"],
        distro=config["distro"],
        rosinstall_filename="fix.rosinstall",
        build_command=config["build_command"],
        apt_packages=config.get("apt_packages", []),
        cuda_version=config.get("cuda_version", 0),
    )


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


def build_all_images() -> None:
    for experiment_filename in find_configs():
        build_images_for_experiment(experiment_filename)


def main(args: t.Optional[t.Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser("Builds Docker images for experiments")
    parser.add_argument('kind', type=str, choices=['recovery', 'detection', 'all'],
                        help='The kind of experiment (recovery or detection')
    parser.add_argument('system', type=str, default="all", help='The system to use')
    parsed_args = parser.parse_args(args)
    if parsed_args.kind == "all":
        if parsed_args.experiment == "all":
            build_all_images()
    else:
        build_images_for_experiment(configuration_to_experiment_file(parsed_args.kind, parsed_args.system))


if __name__ == "__main__":
    main()
