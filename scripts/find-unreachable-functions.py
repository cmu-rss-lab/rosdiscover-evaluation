#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This helper script produces a summary of the unreachable functions in a given node model.
"""
import argparse
import json
import os
import typing as t

from loguru import logger
logger.remove()

from rosdiscover.recover.loader import SymbolicProgramLoader
import rosdiscover

from common.config import (
    RecoveryExperimentConfig,
    load_config_from_file,
)



def find_unreachables(
    system: str,
    package: str,
    node: str
) -> None:
    experiment_directory = os.path.join(
        os.path.dirname(__file__),
        "..",
        "experiments/recovery/subjects",
        system,
    )

    # locate the experiment config for this system
    config_filename = os.path.join(
        experiment_directory,
        "experiment.yml",
    )
    config = load_config_from_file(config_filename)

    # locate the saved model file
    model_filename = os.path.join(
        experiment_directory,
        "models",
        f"{package}__{node}.json",
    )

    # locate the rosdiscover config
    rosdiscover_config_filename = config["config_with_node_sources_filename"]
    rosdiscover_config = rosdiscover.Config.load(rosdiscover_config_filename)

    with open(model_filename, "r") as fh:
        model = json.load(fh)
        node = model["node-name"]
        package = model["package"]["name"]
        loader = SymbolicProgramLoader.for_config(rosdiscover_config)
        program = loader.load(model["program"])
        unreachable_functions = program.unreachable_functions

        for function in unreachable_functions:
            print(f"* {function.name}")


def main() -> None:
    parser = argparse.ArgumentParser("produces a summary of unreachable functions")
    parser.add_argument("system", help="the name of the system")
    parser.add_argument("package", help="the name of the package")
    parser.add_argument("node", help="the name of the node")
    args = parser.parse_args()

    find_unreachables(args.system, args.package, args.node)


if __name__ == "__main__":
    main()
