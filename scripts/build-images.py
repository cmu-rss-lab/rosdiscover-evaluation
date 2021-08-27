#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script builds all of the Docker images for a given experiment."""
import argparse
import os
import subprocess
import typing as t

from common.config import (
    DetectionExperimentConfig,
    RecoveryExperimentConfig,
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
) -> None:
    assert os.path.isabs(rootfs)
    assert os.path.exists(rootfs)

    if not apt_packages:
        apt_packages = []

    apt_packages_arg = " ".join(apt_packages)

    command_args = ["docker", "build", "-f", DOCKERFILE_PATH]
    command_args += ["-t", image]
    command_args += ["--build-arg", "COMMON_ROOTFS", "docker/rootfs"]
    command_args += ["--build-arg", "APT_PACKAGES", f"'{apt_packages_arg}'"]
    command_args += ["--build-arg", "BUILD_COMMAND", build_command]
    command_args += ["--build-arg", "DIRECTORY", directory]
    command_args += ["--build-arg", "ROSINSTALL_FILENAME", rosinstall_filename]
    command_args += ["--build-arg", "DISTRO", distro]
    commands_args += ["."]

    subprocess.check_call(" ".join(command_args), cwd=EVALUATION_DIR, shell=True)


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
    build_images_for_experiment(parsed_args.filename)


if __name__ == "__main__":
    main()
