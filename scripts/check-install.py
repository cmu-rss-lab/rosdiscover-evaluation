#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is used to perform a few basic checks to ensure that the
replication package has been correctly installed.
"""
import typing as t
import subprocess

import docker

from common.images import (
    find_installed_images,
    find_missing_images,
)


def check() -> None:
    which_jq = subprocess.run(
        "which jq",
        shell=True,
        capture_output=True,
        text=True,
    )
    if which_jq.returncode == 0:
        jq_status = f"Yes ({which_jq.stdout.strip()})"
    else:
        jq_status = "No"
    print(f"Is jq installed? {jq_status}\n")

    print("The following evaluation dataset images have been successfully installed:")
    for image in find_installed_images():
        print(f"* {image}")

    print("\nThe following evaluation dataset images are missing:")
    for image in find_missing_images():
        print(f"* {image}")


if __name__ == "__main__":
    check()
