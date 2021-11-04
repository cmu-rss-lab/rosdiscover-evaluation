#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import csv

import typing as t

import attr
import yaml
from loguru import logger

from common.acme import THINGS_TO_IGNORE
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

    def _write_node_element_info(self, f, node, elements, prefix, highlights=None):
        sorted_elements = [t[1] for t in elements if t[0] == node]
        if highlights:
            for h in highlights:
                if h in sorted_elements:
                    sorted_elements.remove(h)
                    sorted_elements.append(h.upper())
        sorted_elements.sort()
        f.write(f"    {prefix}: {', '.join(sorted_elements)}\n")

    def write_publishers_for_node(self, f, node: NamePair, prefix: str = "Publishers", highlights: t.List[str] = None):
        self._write_node_element_info(f, node[1][1:], self.publishers, prefix, highlights)

    def write_subscribers_for_node(self, f, node: NamePair, prefix: str = "Subscribers",
                                   highlights: t.List[str] = None):
        self._write_node_element_info(f, node[1][1:], self.subscribers, prefix, highlights)

    def write_providers_for_node(self, f, node: NamePair, prefix: str = "Providers", highlights: t.List[str] = None):
        self._write_node_element_info(f, node[1][1:], self.providers, prefix, highlights)

    def write_action_clients_for_node(self, f, node: NamePair, prefix: str = "Action Clients",
                                      highlights: t.List[str] = None):
        self._write_node_element_info(f, node[1][1:], self.action_clients, prefix, highlights)

    def write_action_servers_for_node(self, f, node: NamePair, prefix: str = "Action Servers",
                                      highlights: t.List[str] = None):
        self._write_node_element_info(f, node[1][1:], self.action_servers, prefix, highlights)

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
) -> t.Tuple[str, t.Sequence[str]]:
    observed_not_recovered = list(observed.difference(recovered))
    recovered_not_observed = list(recovered.difference(observed))
    observed_not_recovered.sort(key=lambda x: x[0])
    recovered_not_observed.sort(key=lambda x: x[0])

    # Over-approximation - the percentage of elements in the recovered that aren't in the observed
    # Under-approximation - the percentage of elements in the observed that aren't recovered
    rec_err = len(observed_not_recovered)
    obs_err = len(recovered_not_observed)
    differences = f"\n{kind} in observed that aren't in recovered ({rec_err} differences): "
    differences += ", ".join(f"{o[0]}{joiner}{o[1]}" for o in observed_not_recovered)
    differences += f"\n{kind} in recovered that aren't in observed ({obs_err} differences: "
    differences += ", ".join(f"{o[0]}{joiner}{o[1]}" for o in recovered_not_observed)

    if len(recovered) != 0 and len(observed) == 0:
        differences += f"\nRecovered {len(recovered)} but observed nothing"
    if len(observed) > 0:
        differences += f"\nOver approximation = {obs_err / len(observed) * 100}% more than ground truth"
        differences += f"\nUnder approximation = {rec_err / len(observed) * 100}% less than ground truth"
    if obs_err == 0 and rec_err == 0:
        differences += f"\nPerfect match"
        # differences += f"\nScore: {rec_err + obs_err} differences from "
        # differences += f"{len(observed)} ground truth = "
        # differences += f"{(len(observed) - rec_err - obs_err) / len(observed) * 100}% recovered"

    # , kind, #o, #r, #o!r, #r!o, over apprx, under appx
    csv_line = [kind, len(observed), len(recovered), rec_err, obs_err]
    if len(observed) > 0:
        csv_line.extend([obs_err / len(observed), rec_err / len(observed)])
    else:
        csv_line.extend(["NaN", "NaN"])
    return differences, csv_line


def safe_dict_add(dict_, key1, key2, val):
    if key1 not in dict_:
        dict_[key1] = {}
    dict_[key1][key2] = val


def filter_actions_from_observed(summary: ArchitectureSummary):
    """
    Takes topics from observed publishers that are associated with actions and
    remove them from list and add them as actions
    """

    filter_actions_from_recovered(summary)

    if not summary.action_servers and not summary.action_clients:
        # Maybe this was an observed architecture, so we need to extract these
        potential_server_feedbacks = [f for f in summary.publishers if f[1].endswith('/feedback')]
        # potential_server_results = [f for f in summary.publishers if f[1].endswith('/result')]
        # potential_server_statuses = [f for f in summary.publishers if f[1].endswith('/status')]
        # potential_server_goals = [f for f in summary.subscribers if f[1].endswith('/goal')]
        # potential_server_cancels = [f for f in summary.subscribers if f[1].endswith('/cancel')]

        potential_servers = {(n[0], '/'.join(n[1].split('/')[:-1])) for n in potential_server_feedbacks}
        for i in potential_servers:
            result = (i[0], f"{i[1]}/result") in summary.publishers
            status = (i[0], f"{i[1]}/status") in summary.publishers
            goal = (i[0], f"{i[1]}/goal") in summary.subscribers
            cancel = (i[0], f"{i[1]}/cancel") in summary.subscribers

            if result and status and goal and cancel:
                summary.action_servers.add((i[0], i[1]))

        potential_client_feedbacks = [f for f in summary.subscribers if f[1].endswith('/feedback')]
        # potential_client_results = [f for f in summary.subscribers if f[1].endswith('/result')]
        # potential_client_statuses = [f for f in summary.subscribers if f[1].endswith('/status')]
        # potential_client_goals = [f for f in summary.publishers if f[1].endswith('/goal')]
        # potential_client_cancels = [f for f in summary.publishers if f[1].endswith('/cancel')]

        potential_clients = {(n[0], '/'.join(n[1].split('/')[:-1])) for n in potential_client_feedbacks}
        for i in potential_clients:
            result = (i[0], f"{i[1]}/result") in summary.subscribers
            status = (i[0], f"{i[1]}/status") in summary.subscribers
            goal = (i[0], f"{i[1]}/goal") in summary.publishers
            cancel = (i[0], f"{i[1]}/cancel") in summary.publishers

            if result and status and goal and cancel:
                summary.action_clients.add((i[0], i[1]))


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
    comparison_csv = os.path.join(config_directory, "observed.recoverd.compare.csv")
    errors_both_csv = os.path.join(config_directory, "observed.recovered.errors.csv")
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

    observed_summary = extract_architecture_summary(observed_architecture)
    recovered_summary = extract_architecture_summary(recovered_architecture)

    filter_actions_from_observed(observed_summary)
    filter_actions_from_recovered(recovered_summary)

    nodecomp, nodecsv = compare_sets("Nodes", "/", observed_summary.nodes, recovered_summary.nodes)
    pubcomp, pubcsv = compare_sets("Publishers", "->", observed_summary.publishers, recovered_summary.publishers)
    subcomp, subcsv = compare_sets("Subscribers", "<-", observed_summary.subscribers, recovered_summary.subscribers)
    provcomp, provcsv = compare_sets("Providers", ":", observed_summary.providers, recovered_summary.providers)
    accomp, accsv = compare_sets("Action Clients", "^-", observed_summary.action_clients,
                                 recovered_summary.action_clients)
    ascomp, ascsv = compare_sets("Action Servers", "-^", observed_summary.action_servers,
                                 recovered_summary.action_servers)
    with open(comparison_file, 'w') as f:

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
            node_infos = [n for n in recovered_architecture if n['fullname'] == node[1]]
            filename = node_infos[0]['filename']  # if len(node_infos) > 1 else "unknown"
            prov = node_infos[0]['provenance'][0]  # if len(node_infos) > 1 else "U"

            f.write(f"  Node: {node[1]}({prov}) <- "
                    f"{filename}"
                    f":\n")
            node_name = node[1][1:]
            observed_summary.write_publishers_for_node(f, node, "Observed Pubs",
                                                       [t[1] for t in recovered_summary.publishers if
                                                        t[0] == node_name])
            recovered_summary.write_publishers_for_node(f, node, "Recovered Pubs",
                                                        [t[1] for t in observed_summary.publishers if
                                                         t[0] == node_name])
            observed_summary.write_subscribers_for_node(f, node, "Observed Subs",
                                                        [t[1] for t in recovered_summary.subscribers if
                                                         t[0] == node_name])
            recovered_summary.write_subscribers_for_node(f, node, "Recovered Subs",
                                                         [t[1] for t in observed_summary.subscribers if
                                                          t[0] == node_name])
            observed_summary.write_providers_for_node(f, node, "Observed Provs",
                                                      [t[1] for t in recovered_summary.providers if t[0] == node_name])
            recovered_summary.write_providers_for_node(f, node, "Recovered Provs",
                                                       [t[1] for t in observed_summary.providers if t[0] == node_name])
            observed_summary.write_action_servers_for_node(f, node, "Observed Action Servers",
                                                           [t[1] for t in recovered_summary.action_servers if
                                                            t[0] == node_name])
            recovered_summary.write_action_servers_for_node(f, node, "Recovered Action Servers",
                                                            [t[1] for t in observed_summary.action_servers if
                                                             t[0] == node_name])
            observed_summary.write_action_clients_for_node(f, node, "Observed Action Clients",
                                                           [t[1] for t in recovered_summary.action_clients if
                                                            t[0] == node_name])
            recovered_summary.write_action_clients_for_node(f, node, "Recovered Action Clients",
                                                            [t[1] for t in observed_summary.action_clients if
                                                             t[0] == node_name])

        f.write("\n")
        f.write("Differences:\n")
        f.write("============\n")

        f.write(nodecomp)
        f.write(pubcomp)
        f.write(subcomp)
        f.write(provcomp)
        f.write(accomp)
        f.write(ascomp)
        f.write("\nCannot observe service clients")

    # process the errors
    observed_errors = get_acme_errors(os.path.join(config_directory, "logs", "acme-and-check-observed.log"))
    recovered_errors = get_acme_errors(os.path.join(config_directory, "logs", "acme-and-check-recovered.log"))

    with open(comparison_csv, 'w') as f:
        writer = csv.writer(f)
        first = True

        for i in (nodecsv, pubcsv, subcsv, provcsv, accsv, ascsv):
            line = [config['subject']]
            if first:
                if len(observed_errors) > len(recovered_errors):
                    same = len(observed_errors.intersection(recovered_errors)) == len(observed_errors) - len(
                        recovered_errors)
                else:
                    same = len(recovered_errors.intersection(observed_errors)) == len(recovered_errors) - len(
                        observed_errors)
                line += i
                line += [len(observed_errors), len(recovered_errors), same]
                first = False
            else:
                line += i
            writer.writerow(line)

    with open(errors_both_csv, 'w') as f:
        writer = csv.writer(f)
        for i in observed_errors:
            writer.writerow([config['subject'], "observed", i])
        for i in recovered_errors:
            writer.writerow([config['subject'], "recovered", i])


def get_acme_errors(observed_error_log):
    observed_errors = set()
    with open(observed_error_log) as f:
        lines = f.readlines()
        i = len(lines) - 1
        while i != 0 and not 'The following problems' in lines[i] and not 'has no errors' in lines[i]:
            observed_errors.add(lines[i].split(' -     ')[1])
            i = i - 1
    return observed_errors


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
    for ignore in THINGS_TO_IGNORE.split('\n'):
        if ignore.startswith("*") and name.endswith(ignore[1:]):
            return False
        if ignore == name:
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
