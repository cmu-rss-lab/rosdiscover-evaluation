#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to build the .rosinstall files for a given experiment."""
from datetime import datetime, timezone
import argparse
import os
import subprocess
import typing as t

from loguru import logger
import git
import yaml

from common.config import (
    DetectionExperimentConfig,
    EVALUATION_DIR,
    ExperimentConfig,
    RecoveryExperimentConfig,
    RepoVersion,
    load_config_from_file,
)
from common.find_package_dependencies import find_all_package_dependencies

RGTM_DIR = os.path.join(EVALUATION_DIR, "deps/rosinstall_generator_time_machine")
RGTM_PATH = os.path.join(RGTM_DIR, "rosinstall_generator_tm.sh")
WORK_DIR = os.path.join(EVALUATION_DIR, ".workdir")
WORK_REPO_DIR = os.path.join(EVALUATION_DIR, ".workdir", ".repos")


def repo_dir(name: str) -> str:
    return os.path.join(WORK_REPO_DIR, name)


def clone_repos(repos: t.Collection[RepoVersion]) -> None:
    os.makedirs(WORK_REPO_DIR, exist_ok=True)
    for repo_version in repos:
        repo_path = repo_dir(repo_version["name"])
        repo_url = repo_version["url"]

        if not os.path.exists(repo_path):
            logger.info(f"cloning repo: {repo_url}")
            repo = git.Repo.clone_from(repo_url, repo_path)
            logger.info(f"cloned repo: {repo_url}")
        else:
            logger.info(f"repo already cloned: {repo_url}")


def checkout_repos(repos: t.Collection[RepoVersion]) -> None:
    for repo_version in repos:
        path = repo_dir(repo_version["name"])
        url = repo_version["url"]
        version = repo_version["version"]
        repo = git.Repo(path)
        logger.info(f"checking out repo [{url}] to version: {version}")
        git.Git(path).checkout(version)
        for submodule in repo.submodules:
            submodule.update(init=True, recursive=True)
        logger.info(f"checked out repo [{url}] to version: {version}")


def find_repo_package_dependencies(repos: t.Collection[RepoVersion]) -> t.Collection[str]:
    deps: t.Set[str] = set()
    for repo_version in repos:
        path = repo_dir(repo_version["name"])
        deps.update(find_all_package_dependencies(path))
    return deps


def determine_time_machine_datetime(repos: t.Collection[RepoVersion]) -> str:
    logger.info("determining datetime for RGTM...")
    latest = None
    for repo_version in repos:
        repo_path = repo_dir(repo_version["name"])
        repo = git.Repo(repo_path)
        commit = repo.commit(repo_version["version"])
        commit_datetime = commit.authored_datetime
        if latest is None:
            latest = commit_datetime
        else:
            latest = max(commit_datetime, latest)
    assert latest is not None
    iso_datetime = latest.isoformat()
    logger.info(f"determined datetime for RGTM: {iso_datetime}")
    return iso_datetime


def rosinstall(
    distro: str,
    iso_datetime: str,  # ISO 8601 datetime
    packages: t.Collection[str],
    exclude_packages: t.Optional[t.Collection[str]],
    save_to: str,
) -> None:
    command_args = ["yes", "|"]
    command_args += [RGTM_PATH, iso_datetime, distro]
    command_args += packages
    command_args += ["--deps", "--tar"]
    if exclude_packages:
        command_args += ["--exclude"]
        command_args += exclude_packages
    command_args += [ "|", "sed", "-e", "'s/geometry_experimental-release/geometry2-release/g'"]
    command = " ".join(command_args)

    logger.info(f"running RGTM: {command}")
    output = subprocess.check_output(command, shell=True, encoding="utf8")
    logger.info(f"finished RGTM:\n{output}")

    with open(save_to, "w") as fh:
        fh.write(output)


def obtain_rosinstall_for_repo_versions(
    distro: str,
    repos: t.Collection[RepoVersion],
    extra_packages: t.Optional[t.Collection[str]],
    exclude_packages: t.Optional[t.Collection[str]],
    output_filename: str,
) -> None:
    assert repos
    assert os.path.isabs(output_filename)

    if not extra_packages:
        extra_packages = []

    clone_repos(repos)
    checkout_repos(repos)
    logger.info("finding repo package dependencies...")
    repo_package_deps = sorted(find_repo_package_dependencies(repos))
    logger.info(f"found repo package dependencies: {', '.join(repo_package_deps)}")

    iso_datetime = determine_time_machine_datetime(repos)

    # use the time machine to create a .rosinstall file for the deps
    deps: t.Set[str] = set(repo_package_deps).union(extra_packages)
    rosinstall(distro, iso_datetime, deps, exclude_packages, output_filename)

    # add the system under test to the generated .rosinstall file
    with open(output_filename, "r") as fh:
        rosinstall_contents = yaml.safe_load(fh)

    logger.debug(f"adding SUT to .rosinstall file: {output_filename}")
    rosinstall_contents += [
        {"git": {
            "local-name": repo_version["name"],
            "uri": repo_version["url"],
            "version": repo_version["version"],
        }} for repo_version in repos
    ]

    with open(output_filename, "w") as fh:
        yaml.dump(rosinstall_contents, fh, default_flow_style=False)

    logger.debug(f"generated .rosinstall file: {output_filename}")


def obtain_rosinstall_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    extra_packages = config.get("missing_ros_packages", [])
    exclude_packages = config.get("exclude_ros_packages", [])
    output_filename = os.path.join(config["directory"], "pkgs.rosinstall")
    obtain_rosinstall_for_repo_versions(
        distro=config["distro"],
        repos=config["repositories"],
        extra_packages=extra_packages,
        output_filename=output_filename,
        exclude_packages=exclude_packages,
    )


def obtain_rosinstall_for_detection_experiment(config: DetectionExperimentConfig) -> None:
    extra_packages = config.get("missing_ros_packages", [])
    exclude_packages = config.get("exclude_ros_packages", [])
    bug_rosinstall_filename = os.path.join(config["directory"], "bug.rosinstall")
    fix_rosinstall_filename = os.path.join(config["directory"], "fix.rosinstall")

    obtain_rosinstall_for_repo_versions(
        distro=config["distro"],
        repos=config["buggy"]["repositories"],
        extra_packages=extra_packages,
        output_filename=bug_rosinstall_filename,
        exclude_packages=exclude_packages,
    )
    obtain_rosinstall_for_repo_versions(
        distro=config["distro"],
        repos=config["fixed"]["repositories"],
        extra_packages=extra_packages,
        output_filename=fix_rosinstall_filename,
        exclude_packages=exclude_packages,
    )


def obtain_rosinstall_for_experiment(filename: str) -> None:
    config: ExperimentConfig = load_config_from_file(filename)
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

    filename = parsed_args.filename
    logger.info(f"obtaining .rosinstall files for experiment: {filename}")
    obtain_rosinstall_for_experiment(filename)
    logger.info(f"obtained .rosinstall files for experiment: {filename}")


if __name__ == "__main__":
    main()
