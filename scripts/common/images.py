# -*- coding: utf-8 -*-
__all__ = (
    "find_all_docker_image_names",
    "find_all_known_docker_image_names",
    "find_docker_images_for_experiment",
    "find_installed_images",
    "find_missing_images",
    "find_named_volumes",
)

import typing as t

import docker

from .config import (
    load_config_from_file,
    find_configs,
)

def find_docker_images_for_experiment(filename: str) -> t.Set[str]:
    config = load_config_from_file(filename)
    if config["type"] == "detection":
        return set([config["buggy"]["docker"]["image"], config["fixed"]["docker"]["image"]])
    elif config["type"] == "recovery":
        return set([config["docker"]["image"]])
    else:
        raise ValueError("unexpected experiment type")


def find_all_docker_image_names() -> t.Set[str]:
    image_names = set()
    for experiment_filename in find_configs():
        image_names.update(find_docker_images_for_experiment(experiment_filename))
    return image_names


def find_all_known_docker_image_names() -> t.Set[str]:
    client = docker.from_env()
    known_image_names = set()
    for known_image in client.images.list():
        known_image_names.update(known_image.tags)
    return known_image_names


def find_missing_images() -> t.Set[str]:
    docker_image_names = find_all_docker_image_names()
    known_image_names = find_all_known_docker_image_names()
    return docker_image_names.difference(known_image_names)


def find_installed_images() -> t.Set[str]:
    docker_image_names = find_all_docker_image_names()
    missing_images = find_missing_images()
    return docker_image_names.difference(missing_images)


def find_named_volumes() -> t.Set[str]:
    client = docker.from_env()
    named_volumes = set()
    for named_volume in client.volumes.list():
        named_volumes.add(named_volume.name)
    return named_volumes
