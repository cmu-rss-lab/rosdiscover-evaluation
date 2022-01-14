#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is used to bundle all of the Docker images from these experiments
into a single .tar archive. The images can be installed directly from that
archive via docker load without the need to rebuild them from scratch.
"""
from timeit import default_timer as timer
import os
import subprocess
import sys
import typing as t

from loguru import logger
import docker

logger.remove()

from common.config import (
    DetectionExperimentConfig,
    EVALUATION_DIR,
    RecoveryExperimentConfig,
    find_configs,
    load_config_from_file,
)
from common.images import (
    find_all_docker_image_names,
    find_all_known_docker_image_names,
    find_docker_images_for_experiment,
    find_missing_images,
)

DOCKER_DIR = os.path.join(EVALUATION_DIR, "docker")


def main() -> None:
    stderr_logger = logger.add(
        sys.stderr,
        colorize=True,
        format="<bold><level>{level}:</level></bold> {message}",
        level="DEBUG",
    )

    archive_filename = os.path.join(DOCKER_DIR, "images.tar")

    # find the names of all of the Docker images
    docker_image_names = find_all_docker_image_names()
    logger.info(f"found {len(docker_image_names)} docker images: {', '.join(docker_image_names)}")

    # omit any missing images
    known_image_names = find_all_known_docker_image_names()
    logger.info(f"found {len(known_image_names)} tagged Docker images on machine: {', '.join(known_image_names)}")

    missing_images = docker_image_names.difference(known_image_names)
    if missing_images:
        logger.warning(f"missing {len(missing_images)} images: {', '.join(missing_images)}")

    present_images = docker_image_names.difference(missing_images)
    if not present_images:
        logger.error("no images are installed")
        sys.exit(1)

    logger.info(f"adding {len(present_images)} installed images to the archive: {', '.join(present_images)}")

    command_args = [
        "docker",
        "save",
        "-o",
        archive_filename,
    ]
    command_args += present_images
    command = " ".join(command_args)

    logger.debug(f"running command: {command_args}")

    time_start = timer()
    subprocess.run(command, shell=True, stdin=subprocess.DEVNULL, check=True)
    time_stop = timer()
    duration = time_stop - time_start
    logger.info(f"finished building archive [{archive_filename}]: took {duration:.2f} seconds")


if __name__ == "__main__":
    main()
