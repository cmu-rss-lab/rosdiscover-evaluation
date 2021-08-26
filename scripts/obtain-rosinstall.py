#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script is used to build the .rosinstall files for a given experiment."""
import argparse
import os
import typing as t


class RepoVersion(t.TypedDict):
    name: str
    url: str
    release: str


def obtain_rosinstall_for_repo_versions(
    repos: t.Collection[RepoVersion],
    output_filename: str,
) -> None:
    assert repos
    assert os.path.isabs(output_filename)
    raise NotImplementedError
