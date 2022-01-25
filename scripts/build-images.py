#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script builds all of the Docker images for a given experiment."""
import argparse
import os
import subprocess
import typing as t

from loguru import logger

from common.config import (
    DetectionExperimentConfig,
    EVALUATION_DIR,
    ExperimentConfig,
    find_configs,
    load_config,
    load_config_from_file,
    RecoveryExperimentConfig,
)

DOCKER_DIR = os.path.join(EVALUATION_DIR, "docker")
DOCKERFILE_PATH = os.path.join(DOCKER_DIR, "Dockerfile")


def _build_image_via_command(image: str, command: str) -> bool:
    logger.info(f"building image [{image}]: {command}")
    outcome = subprocess.run(command, cwd=EVALUATION_DIR, shell=True)
    if outcome.returncode == 0:
        logger.info(f"successfully built image: {image}")
    else:
        logger.error(f"failed to build image: {image}")


def build_custom_image(
    image: str,
    directory: str,
    docker_filename: str,
    docker_context: str,
) -> None:
    assert not os.path.isabs(docker_filename)
    assert not os.path.isabs(docker_context)
    docker_filename = os.path.join(directory, docker_filename)
    docker_context = os.path.join(directory, docker_context)

    command = " ".join([
        "docker",
        "build",
        "-f",
        docker_filename,
        "-t",
        image,
        docker_context,
    ])
    _build_image_via_command(image, command)


def build_templated_image(
    image: str,
    directory: str,
    distro: str,
    rosinstall_filename: str,
    build_command: str,
    apt_packages: t.Optional[t.Sequence[str]],
    cuda_version: str,
) -> None:
    assert os.path.exists(directory)

    if not apt_packages:
        apt_packages = []
    apt_packages_arg = " ".join(apt_packages)

    logger.info(f"apt_packages_arg: {apt_packages_arg}")

    rel_experiment_dir = os.path.relpath(directory, EVALUATION_DIR)
    os.makedirs(os.path.join(directory, "docker"), exist_ok=True)

    command_args = ["docker", "build", "-f", DOCKERFILE_PATH]
    command_args += ["--build-arg", "COMMON_ROOTFS=docker/rootfs"]
    command_args += ["--build-arg", f"CUDA_VERSION='{cuda_version}'"]
    command_args += ["--build-arg", f"APT_PACKAGES='{apt_packages_arg}'"]
    command_args += ["--build-arg", f"BUILD_COMMAND='{build_command}'"]
    command_args += ["--build-arg", f"DIRECTORY={rel_experiment_dir}"]
    command_args += ["--build-arg", f"ROSINSTALL_FILENAME={rosinstall_filename}"]
    command_args += ["--build-arg", f"DISTRO={distro}"]
    command_args += ["."]
    command_args += ["-t", image]
    command = " ".join(command_args)
    _build_image_via_command(image, command)


def build_images_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    logger.info(f"building images for recovery experiment: {config['filename']}")
    image_name = config["docker"]["image"]
    image_type = config["docker"]["type"]

    if image_type == "custom":
        build_custom_image(
            image=image_name,
            directory=config["directory"],
            docker_filename=config["docker"].get("filename", "Dockerfile"),
            docker_context=config["docker"].get("context", "."),
        )
    elif image_type == "templated":
        build_templated_image(
            image=image_name,
            directory=config["directory"],
            distro=config["distro"],
            rosinstall_filename="pkgs.rosinstall",
            build_command=config["build_command"],
            apt_packages=config.get("apt_packages", []),
            cuda_version=config.get("cuda_version", "0"),
        )
    else:
        raise ValueError(f"unknown docker type: {image_type}")


def build_images_for_detection_experiment(config: DetectionExperimentConfig) -> None:
    logger.info(f"building images for detection experiment: {config['filename']}")
    for version in ("buggy", "fixed"):
        image_type = config[version]["docker"]["type"]
        image_name = config[version]["docker"]["image"]
        if version == "buggy":
            rosinstall_filename = "bug.rosinstall"
        else:
            rosinstall_filename = "fix.rosinstall"
        if image_type == "templated":
            build_templated_image(
                image=image_name,
                directory=config["directory"],
                distro=config["distro"],
                rosinstall_filename=rosinstall_filename,
                build_command=config["build_command"],
                apt_packages=config.get("apt_packages", []),
                cuda_version=config.get("cuda_version", "0"),
            )
        elif image_type == "custom":
            build_custom_image(
                image=image_name,
                directory=config["directory"],
                docker_filename=config[version]["docker"].get("filename", "Dockerfile"),
                docker_context=config[version]["docker"].get("context", "."),
            )
        else:
            raise ValueError(f"unknown docker type: {image_type}")



def build_images_for_experiment(kind: str, system: str, experiment_file: str) -> None:
    logger.info(f"building images for experiment: {kind} / {system}")
    config: ExperimentConfig = load_config(kind, system, experiment_file)
    build_images_for_experiment_config(config)


def build_images_for_experiment_config(config):
    if config["type"] == "detection":
        build_images_for_detection_experiment(config)
    elif config["type"] == "recovery":
        build_images_for_recovery_experiment(config)
    else:
        raise ValueError(f"unknown experiment type: {config['type']}")
    logger.info(f"built images for experiment: {config['filename']}")


def build_all_images(directory: t.Optional[str] = None) -> None:
    """Builds all images; optionally builds only those under a given directory.

    Arguments
    ---------
    directory: str, optional
        optionally gives the path of a directory, relative to the root of the
        evaluation repository that should be used to restrict which images are
        built.
    """
    for experiment_filename in find_configs(directory):
        config: ExperimentConfig = load_config_from_file(experiment_filename)
        build_images_for_experiment_config(config)


def build_all_recovery_images() -> None:
    build_all_images(directory="experiments/recovery")


def build_all_detection_images() -> None:
    build_all_images(directory="experiments/detection")


def main(args: t.Optional[t.Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser("Builds Docker images for experiments")
    parser.add_argument(
        'kind',
        choices=['recovery', 'detection'],
        help='The kind of experiment (i.e., recovery or detection)',
    )
    parser.add_argument(
        'system',
        default="all",
        help='The name of system to use (e.g., autorally, turtlebot, husky)',
    )
    parsed_args = parser.parse_args(args)

    if parsed_args.system == "all":
        {
            "recovery": build_all_recovery_images,
            "detection": build_all_detection_images,
        }[parsed_args.kind]()
    else:
        build_images_for_experiment(parsed_args.kind, parsed_args.system, "experiment.yml")


if __name__ == "__main__":
    main()
