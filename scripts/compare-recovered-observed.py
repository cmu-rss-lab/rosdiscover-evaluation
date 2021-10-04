#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys

import typing as t

import yaml
from loguru import logger

from common.config import ExperimentConfig, load_config


def compare_sets(
    kind: str,
    joiner: str,
    observed: t.Set[t.Tuple[str, str]],
    recovered: t.Set[t.Tuple[str, str]],
) -> str:
    observed_not_recovered = list(observed.difference(recovered))
    recovered_not_observed = list(recovered.difference(observed))
    observed_not_recovered.sort(key=lambda x: x[0])
    recovered_not_observed.sort(key=lambda x: x[0])

    differences = f"\n{kind} in observed that aren't in recovered: "
    differences += ", ".join(f"{o[0]}{joiner}{o[1]}" for o in observed_not_recovered)
    differences += f"\n{kind} in recovered that aren't in observed: "
    differences += ", ".join(f"{o[0]}{joiner}{o[1]}" for o in recovered_not_observed)

    return differences


def safe_dict_add(dict_, key1, key2, val):
    if key1 not in dict_:
        dict_[key1] = {}
    dict_[key1][key2] = val


def filter_actions_from_observed(observed_publishers, observed_action_servers, observed_action_clients):
    """
    Takes topics from observed publishers that are associated with actions and
    remove them from list and add them as actions
    """
    pass


def filter_actions_from_recovered(recovered_publishers,
                                  recovered_subscribers,
                                  recovered_action_servers,
                                  recovered_action_clients):

    for server in recovered_action_servers:
        node = server[0]
        act_srv = server[1]
        recovered_publishers.remove((node, f"{act_srv}/feedback"))
        recovered_publishers.remove((node, f"{act_srv}/result"))
        recovered_publishers.remove((node, f"{act_srv}/status"))
        recovered_subscribers.remove((node, f"{act_srv}/goal"))
        recovered_subscribers.remove((node, f"{act_srv}/cancel"))

    for client in recovered_action_clients:
        node = client[0]
        act_clt = client[1]
        recovered_subscribers.remove((node, f"{act_clt}/feedback"))
        recovered_subscribers.remove((node, f"{act_clt}/result"))
        recovered_subscribers.remove((node, f"{act_clt}/status"))
        recovered_publishers.remove((node, f"{act_clt}/goal"))
        recovered_publishers.remove((node, f"{act_clt}/cancel"))


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
    with open(observed_yml_file, 'r') as f:
        observed_architecture = yaml.load(f, Loader=yaml.SafeLoader)
    with open(recovered_yml_file, 'r') as f:
        recovered_architecture = yaml.load(f, Loader=yaml.SafeLoader)

    with open(comparison_file, 'w') as f:

        observed_publishers, observed_subscribers, observed_providers, observed_action_clients, observed_action_servers\
            = extract_architecture_elements(observed_architecture)
        recovered_publishers, recovered_subscribers, recovered_providers, recovered_action_clients, \
            recovered_action_servers = extract_architecture_elements(recovered_architecture)

        filter_actions_from_observed(observed_publishers, observed_action_servers, observed_action_clients)
        filter_actions_from_recovered(recovered_publishers, recovered_subscribers, recovered_action_servers,
                                      recovered_action_clients)

        observed_node_names = {("ph", n["fullname"]) for n in observed_architecture}
        recovered_node_names = {("ph", n["fullname"]) for n in recovered_architecture}

        f.write("Observed architecture summary:\n")
        f.write("==============================\n")
        write_architecture_summary(f, observed_node_names, observed_publishers, observed_subscribers,
                                   observed_providers, observed_action_servers, observed_action_clients)
        f.write("\n")
        f.write("Recoverd architecture summary:\n")
        f.write("==============================\n")

        write_architecture_summary(f, recovered_node_names, recovered_publishers, recovered_subscribers,
                                   recovered_providers, recovered_action_servers, recovered_action_clients)

        nodes_in_common = observed_node_names.intersection(recovered_node_names)
        f.write("\n")
        f.write("Side-by-side of common nodes:\n")
        f.write("=============================\n")

        for node in nodes_in_common:
            f.write(f"  Node: {node[1]}:\n")
            write_node_element_info(f, node[1][1:], observed_publishers, "Observed Pubs")
            write_node_element_info(f, node[1][1:], recovered_publishers, "Recovered Pubs")
            write_node_element_info(f, node[1][1:], observed_subscribers, "Observed Subs")
            write_node_element_info(f, node[1][1:], recovered_subscribers, "Recovered Subs")
            write_node_element_info(f, node[1][1:], observed_providers, "Observed Provs")
            write_node_element_info(f, node[1][1:], recovered_providers, "Recovered Provs")
            write_node_element_info(f, node[1][1:], observed_action_servers, "Observed Action Servers")
            write_node_element_info(f, node[1][1:], recovered_action_servers, "Recovered Action Servers")
            write_node_element_info(f, node[1][1:], observed_action_clients, "Observed Action Clients")
            write_node_element_info(f, node[1][1:], recovered_action_clients, "Recovered Action Clients")

        f.write("\n")
        f.write("Differences:\n")
        f.write("============\n")
        f.write(compare_sets("Nodes", "/", observed_node_names, recovered_node_names))
        f.write(compare_sets("Publishers", "->", observed_publishers, recovered_publishers))
        f.write(compare_sets("Subscribers", "<-", observed_subscribers, recovered_subscribers))
        f.write(compare_sets("Providers", ":", observed_providers, recovered_providers))
        f.write(compare_sets("Action Clients", "^-", observed_action_clients, recovered_action_clients))
        f.write(compare_sets("Action Servers", "-^", observed_action_servers, recovered_action_servers))
        f.write("\nCannot observer service clients")


def write_architecture_summary(f, node_names, publishers, subscribers, providers, action_servers, action_clients):
    sorted_node_names = list(node_names)
    sorted_node_names.sort(key=lambda x: x[1])
    for node in node_names:
        f.write(f"  Node: {node[1]}:\n")
        write_node_element_info(f, node[1][1:], publishers, "Publishers")
        write_node_element_info(f, node[1][1:], subscribers, "Subscribers")
        write_node_element_info(f, node[1][1:], providers, "Provides")
        write_node_element_info(f, node[1][1:], action_servers, "Action Servers")
        write_node_element_info(f, node[1][1:], action_clients, "Action Clients")


def write_node_element_info(f, node, elements, prefix):
    sorted_elements = [t[1] for t in elements if t[0] == node]
    sorted_elements.sort()
    f.write(f"    {prefix}: {', '.join(sorted_elements)}\n")


def extract_architecture_elements(
    architecture: t.List[t.Any]
) -> t.Tuple[t.Set[t.Tuple[str, str]],
             t.Set[t.Tuple[str, str]],
             t.Set[t.Tuple[str, str]],
             t.Set[t.Tuple[str, str]],
             t.Set[t.Tuple[str, str]]]:
    publishers: t.Set[t.Tuple[str, str]] = set()
    subscribers: t.Set[t.Tuple[str, str]] = set()
    providers: t.Set[t.Tuple[str, str]] = set()
    action_clients: t.Set[t.Tuple[str, str]] = set()
    action_servers: t.Set[t.Tuple[str, str]] = set()

    for node in architecture:
        for topic in node["pubs"]:
            if include_element(topic):
                publishers.add((node["name"], topic["name"]))
        for topic in node["subs"]:
            if include_element(topic):
                subscribers.add((node["name"], topic["name"]))
        for service in node["provides"]:
            if include_element(service):
                providers.add((node["name"], service["name"]))
        for client in node["action-clients"]:
            action_clients.add((node["name"], client["name"]))
        for server in node["action-servers"]:
            action_servers.add((node["name"], server["name"]))

    return publishers, subscribers, providers, action_clients, action_servers


def include_element(named: t.Dict[str, t.Any]) -> bool:
    name = named["name"]
    if name.endswith("parameter_descriptions"):
        return False
    if name.endswith("parameter_updates"):
        return False
    if name.endswith("set_parameters"):
        return False
    return True


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
