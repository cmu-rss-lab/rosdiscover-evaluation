#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module is used to recursively find the stated dependencies for all ROS packages within a given path."""

__all__ = ("find_all_package_dependencies",)

import os
import typing as t
import xml.etree.ElementTree as ET

from loguru import logger


def find_package_xml_files(directory: str) -> t.Collection[str]:
    found: t.List[str] = []
    for root, _, files in os.walk(directory):
        if "package.xml" in files:
            found.append(os.path.join(root, "package.xml"))
    return found


def find_all_package_dependencies(directory: str) -> t.Set[str]:
    defined_packages: t.MutableSet[str] = set()
    used_packages: t.MutableSet[str] = set()

    for filename in find_package_xml_files(directory):
        tree = ET.parse(filename)
        root = tree.getroot()
        defined_packages.update(t.text for t in root.findall("name"))
        for tag in ("depend", "build_depend", "build_export_depend", "run_depend"):
            used_packages.update(t.text for t in root.findall(tag))

    dependencies = used_packages - defined_packages
    return dependencies
