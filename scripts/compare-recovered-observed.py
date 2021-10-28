#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys

import typing as t

import attr
import yaml
from loguru import logger

from common.acme import TOPICS_TO_IGNORE
from common.config import ExperimentConfig, load_config

NamePair = t.Tuple[str, str]
NamePairSet = t.Set[NamePair]


@attr.s(slots=True, auto_attribs=True)
class ArchitectureSummary:
    nodes: NamePairSet
    publishers: NamePairSet
    subscribers: NamePairSet
    providers: NamePairSet
    action_servers: NamePairSet
    action_clients: NamePairSet

    def _write_node_element_info(self, f, node, elements, prefix):
        sorted_elements = [t[1] for t in elements if t[0] == node]
        sorted_elements.sort()
        f.write(f"    {prefix}: {', '.join(sorted_elements)}\n")

    def write_publishers_for_node(self, f, node: NamePair, prefix: str = "Publishers"):
        self._write_node_element_info(f, node[1][1:], self.publishers, prefix)

    def write_subscribers_for_node(self, f, node: NamePair, prefix: str = "Subscribers"):
        self._write_node_element_info(f, node[1][1:], self.subscribers, prefix)

    def write_providers_for_node(self, f, node: NamePair, prefix: str = "Providers"):
        self._write_node_element_info(f, node[1][1:], self.providers, prefix)

    def write_action_clients_for_node(self, f, node: NamePair, prefix: str = "Action Clients"):
        self._write_node_element_info(f, node[1][1:], self.action_clients, prefix)

    def write_action_servers_for_node(self, f, node: NamePair, prefix: str = "Action Servers"):
        self._write_node_element_info(f, node[1][1:], self.action_servers, prefix)

    def write_to_file(self, f):
        sorted_node_names = list(self.nodes)
        sorted_node_names.sort(key=lambda x: x[1])
        for node in sorted_node_names:
            f.write(f"  Node: {node[1]}:\n")
            self.write_publishers_for_node(f, node)
            self.write_subscribers_for_node(f, node)
            self.write_providers_for_node(f, node)
            self.write_action_servers_for_node(f, node)
            self.write_action_clients_for_node(f, node)


def compare_sets(
    kind: str,
    joiner: str,
    observed: NamePairSet,
    recovered: NamePairSet,
) -> str:
    observed_not_recovered = list(observed.difference(recovered))
    recovered_not_observed = list(recovered.difference(observed))
    observed_not_recovered.sort(key=lambda x: x[0])
    recovered_not_observed.sort(key=lambda x: x[0])

    differences = f"\n{kind} in observed that aren't in recovered: "
    differences += ", ".join(f"{o[0]}{joiner}{o[1]}" for o in observed_not_recovered)
    differences += f"\n{kind} in recovered that aren't in observed: "
    differences += ", ".join(f"{o[0]}{joiner}{o[1]}" for o in recovered_not_observed)
    rec_err = len(observed_not_recovered)
    obs_err = len(recovered_not_observed)
    if len(observed) > 0:
        differences += f"\nScore: {rec_err + obs_err} differences from "
        differences += f"{len(observed)} ground truth = "
        differences += f"{(len(observed) - rec_err - obs_err) / len(observed) * 100}% recovered"
    elif len(recovered) != 0:
        differences += f"\nRecovered {len(recovered)} but observed nothing"
    return differences


def safe_dict_add(dict_, key1, key2, val):
    if key1 not in dict_:
        dict_[key1] = {}
    dict_[key1][key2] = val


def filter_actions_from_observed(summary: ArchitectureSummary):
    """
    Takes topics from observed publishers that are associated with actions and
    remove them from list and add them as actions
    """
    pass


def filter_actions_from_recovered(summary: ArchitectureSummary):
    for server in summary.action_servers:
        node = server[0]
        act_srv = server[1]
        summary.publishers.remove((node, f"{act_srv}/feedback"))
        summary.publishers.remove((node, f"{act_srv}/result"))
        summary.publishers.remove((node, f"{act_srv}/status"))
        summary.subscribers.remove((node, f"{act_srv}/goal"))
        summary.subscribers.remove((node, f"{act_srv}/cancel"))

    for client in summary.action_clients:
        node = client[0]
        act_clt = client[1]
        summary.subscribers.remove((node, f"{act_clt}/feedback"))
        summary.subscribers.remove((node, f"{act_clt}/result"))
        summary.subscribers.remove((node, f"{act_clt}/status"))
        summary.publishers.remove((node, f"{act_clt}/goal"))
        summary.publishers.remove((node, f"{act_clt}/cancel"))


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

        observed_summary = extract_architecture_summary(observed_architecture)
        recovered_summary = extract_architecture_summary(recovered_architecture)

        filter_actions_from_observed(observed_summary)
        filter_actions_from_recovered(recovered_summary)

        f.write("Observed architecture summary:\n")
        f.write("==============================\n")
        observed_summary.write_to_file(f)
        f.write("\n")
        f.write("Recoverd architecture summary:\n")
        f.write("==============================\n")
        recovered_summary.write_to_file(f)
        f.write("Provenance information:\n")
        f.write("-----------------------\n")

        def provenance(p: str) -> t.List[str]:
            return [node['fullname'] for node in recovered_architecture if node['provenance'] == p]

        handwritten = provenance("handwritten")
        recovered = provenance("recovered")
        placeholders = provenance("placeholder")
        unknown = provenance("unknown")
        f.write(f"HANDWRITTEN ({len(handwritten)}): {', '.join(handwritten)}\n")
        f.write(f"RECOVERED ({len(recovered)}): {', '.join(recovered)}\n")
        f.write(f"PLACEHOLDERS ({len(placeholders)}): {', '.join(placeholders)}\n")
        f.write(f"UNKNOWN ({len(unknown)}): {', '.join(unknown)}\n")



        nodes_in_common = observed_summary.nodes.intersection(recovered_summary.nodes)
        f.write("\n")
        f.write("Side-by-side of common nodes:\n")
        f.write("=============================\n")

        for node in nodes_in_common:
            f.write(f"  Node: {node[1]}:\n")
            observed_summary.write_publishers_for_node(f, node, "Observed Pubs")
            recovered_summary.write_publishers_for_node(f, node, "Recovered Pubs")
            observed_summary.write_subscribers_for_node(f, node, "Observed Subs")
            recovered_summary.write_subscribers_for_node(f, node, "Recovered Subs")
            observed_summary.write_providers_for_node(f, node, "Observed Provs")
            recovered_summary.write_providers_for_node(f, node, "Recovered Provs")
            observed_summary.write_action_servers_for_node(f, node, "Observed Action Servers")
            recovered_summary.write_action_servers_for_node(f, node, "Recovered Action Servers")
            observed_summary.write_action_clients_for_node(f, node, "Observed Action Clients")
            recovered_summary.write_action_clients_for_node(f, node, "Recovered Action Clients")

        f.write("\n")
        f.write("Differences:\n")
        f.write("============\n")
        f.write(compare_sets("Nodes", "/", observed_summary.nodes, recovered_summary.nodes))
        f.write(compare_sets("Publishers", "->", observed_summary.publishers, recovered_summary.publishers))
        f.write(compare_sets("Subscribers", "<-", observed_summary.subscribers, recovered_summary.subscribers))
        f.write(compare_sets("Providers", ":", observed_summary.providers, recovered_summary.providers))
        f.write(compare_sets("Action Clients", "^-", observed_summary.action_clients, recovered_summary.action_clients))
        f.write(compare_sets("Action Servers", "-^", observed_summary.action_servers, recovered_summary.action_servers))
        f.write("\nCannot observer service clients")


def extract_architecture_summary(
    architecture: t.List[t.Any]
) -> ArchitectureSummary:
    nodes: NamePairSet = set()
    publishers: NamePairSet = set()
    subscribers: NamePairSet = set()
    providers: NamePairSet = set()
    action_clients: NamePairSet = set()
    action_servers: NamePairSet = set()

    for node in architecture:
        nodes.add(("ph", node["fullname"]))
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

    return ArchitectureSummary(nodes=nodes,
                               publishers=publishers,
                               subscribers=subscribers,
                               providers=providers,
                               action_clients=action_clients,
                               action_servers=action_servers)


def include_element(named: t.Dict[str, t.Any]) -> bool:
    name = named["name"]
    if name.endswith("parameter_descriptions"):
        return False
    if name.endswith("parameter_updates"):
        return False
    if name.endswith("set_parameters"):
        return False
    for ignore in TOPICS_TO_IGNORE.split('\n'):
        if ignore.startswith("*") and named.startswith(ignore[1:]):
            return False
        if ignore == named:
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
