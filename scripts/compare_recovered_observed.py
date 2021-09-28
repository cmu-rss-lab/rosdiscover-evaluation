# -*- coding: utf-8 -*-
import argparse
import os
import sys

import typing as t

import yaml
from loguru import logger

from scripts.common.config import ExperimentConfig, load_config


def compare_sets(
    kind: str,
    joiner: str,
    observed: t.Set[t.Tuple[str, str]],
    recovered: t.Set[t.Tuple[str, str]],
) -> str:
    observed_not_recovered = observed.difference(recovered)
    recovered_not_observed = recovered.difference(observed)

    differences = f"\n{kind} in observed that aren't in recovered: "
    differences += ", ".join(f"{o[0]}{joiner}{o[1]}" for o in observed_not_recovered)
    differences += f"\n{kind} in recovered that aren't in observed: "
    differences += ", ".join(f"{o[0]}{joiner}{o[1]}" for o in recovered_not_observed)

    return differences


def compare(config: ExperimentConfig) -> None:
    if config["type"] != "recovery":
        error('This command only works for "recovery" experiments')

    config_directory = config["directory"]
    observed_yml_file = os.path.join(config_directory, "observed.architecture.yml")
    recovered_yml_file = os.path.join(config_directory, "recovered.architecture.yml")

    comparison_file = os.path.join(config_directory, "compare.observed-recovered.log")

    if not os.path.exists(observed_yml_file):
        error(f"[{observed_yml_file} not found. Perhaps observe-system was not run for "
              f"this configuration.")
    if not os.path.exists(recovered_yml_file):
        error(f"[{recovered_yml_file}] not found. Perhaps recover-system was not run "
              f"for this configuration.")

    observed_architecture = yaml.load(observed_yml_file, Loader=yaml.SafeLoader)
    recovered_architecture = yaml.load(recovered_yml_file, Loader=yaml.SafeLoader)

    with open(comparison_file, 'w') as f:
        observed_node_names = {(n["package"], n["name"]) for n in observed_architecture}
        recovered_node_names = {(n["package"], n["name"]) for n in recovered_architecture}

        f.write(compare_sets("Nodes", "/", observed_node_names, recovered_node_names))

        observed_publishers, observed_subscribers, observed_providers = extract_architecture_elements(
            observed_architecture)
        recovered_publishers, recovered_subscribers, recovered_providers = extract_architecture_elements(
            recovered_architecture)

        f.write(compare_sets("Publishers", "->", observed_publishers, recovered_publishers))
        f.write(compare_sets("Subscribers", "<-", observed_subscribers, recovered_subscribers))
        f.write(compare_sets("Providers", ":", observed_providers, recovered_providers))
        f.write("\nCannot observer service clients")


def extract_architecture_elements(
    architecture: t.List[t.Any]
) -> t.Tuple[t.Set[t.Tuple[str, str]], t.Set[t.Tuple[str, str]], t.Set[t.Tuple[str, str]]]:
    publishers: t.Set[t.Tuple[str, str]] = set()
    subscribers: t.Set[t.Tuple[str, str]] = set()
    providers: t.Set[t.Tuple[str, str]] = set()
    for node in architecture:
        for topic in node["pubs"]:
            publishers.add((node["name"], topic["name"]))
        for topic in node["subs"]:
            subscribers.add((node["name"], topic["name"]))
        for service in node["provides"]:
            providers.add((node["name"], service["name"]))

    return publishers, subscribers, providers


def error(message: str) -> t.NoReturn:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    stderr_logger = logger.add(
        sys.stderr,
        colorize=True,
        format="<bold><level>{level}:</level></bold> {message}",
        level="INFO",
    )
    parser = argparse.ArgumentParser("compare observed and recovered architecture")
    parser.add_argument(
        "configuration",
        help="the path to the configuration file for comparing architectures. "
             "(Note, assumed that observe and recover have been run)",
    )
    args = parser.parse_args()
    experiment_filename: str = args.configuration
    if not os.path.exists(experiment_filename):
        error(f"configuration file not found: {experiment_filename}")
    config = load_config(experiment_filename)
    compare(config)


if __name__ == "__main__":
    main()
