#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import csv
import os
import sys
import typing as t

import attr
import yaml
from loguru import logger

from common.acme import get_acme_errors, THINGS_TO_IGNORE
from common.cli import add_common_options
from common.config import configuration_to_experiment_file, ExperimentConfig, load_config

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
        if not sorted_elements and '/' in node:
            # Hack, this is a compound name. Need to fix it in the elements too
            sorted_elements = [t[1] for t in elements if node.split('/')[-1] == t[0]]
            if sorted_elements:
                for t in elements:
                    if node.split('/')[-1] == t[0]:
                        elements.add((node, t[1]))
                        elements.remove((t[0], t[1]))
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


def provenance(p: str, recovered_architecture) -> t.List[str]:
    return [node['fullname'] for node in recovered_architecture if node['provenance'] == p]


def compare_sets(
    kind: str,
    case: str,
    joiner: str,
    observed: NamePairSet,
    recovered: NamePairSet,
    nodes: t.List[t.Any]
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
    csv_line = [case, kind, len(observed), len(recovered), rec_err, obs_err]
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
    results_directory = config["results_directory"]
    observed_yml_file = os.path.join(results_directory, "observed.architecture.yml")
    recovered_yml_file = os.path.join(results_directory, "recovered.architecture.yml")

    comparison_file = os.path.join(results_directory, "compare.observed-recovered.txt")
    comparison_csv = os.path.join(results_directory, "observed.recovered.compare.csv")
    errors_both_csv = os.path.join(results_directory, "observed.recovered.errors.csv")
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

    nodecomp_all, nodecsv_all = compare_sets("Nodes", "all", "/", observed_summary.nodes, recovered_summary.nodes,
                                             recovered_architecture)
    pubcomp_all, pubcsv_all = compare_sets("Publishers", "all", "->", observed_summary.publishers,
                                           recovered_summary.publishers,
                                           recovered_architecture)
    subcomp_all, subcsv_all = compare_sets("Subscribers", "all", "<-", observed_summary.subscribers,
                                           recovered_summary.subscribers, recovered_architecture)
    provcomp_all, provcsv_all = compare_sets("Providers", "all", ":", observed_summary.providers,
                                             recovered_summary.providers,
                                             recovered_architecture)
    accomp_all, accsv_all = compare_sets("Action Clients", "all", "^-", observed_summary.action_clients,
                                         recovered_summary.action_clients, recovered_architecture)
    ascomp_all, ascsv_all = compare_sets("Action Servers", "all", "-^", observed_summary.action_servers,
                                         recovered_summary.action_servers, recovered_architecture)
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

        handwritten = provenance("handwritten", recovered_architecture)
        recovered = provenance("recovered", recovered_architecture)
        placeholders = provenance("placeholder", recovered_architecture)
        unknown = provenance("unknown", recovered_architecture)
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

        f.write(nodecomp_all)
        f.write(pubcomp_all)
        f.write(subcomp_all)
        f.write(provcomp_all)
        f.write(accomp_all)
        f.write(ascomp_all)
        f.write("\nCannot observe service clients")

    # process the errors
    observed_errors = get_acme_errors(os.path.join(results_directory, "acme-and-check-observed.txt"))
    recovered_errors = get_acme_errors(os.path.join(results_directory, "acme-and-check-recovered.txt"))

    hw_p = set(p[1:] for p in provenance("handwritten", recovered_architecture))
    re_p = set(p[1:] for p in provenance("recovered", recovered_architecture))
    o_p_h = set(n for n in observed_summary.publishers if n[0] in hw_p)
    r_p_h = set(n for n in recovered_summary.publishers if n[0] in hw_p)
    _, pubcsv_hw = compare_sets("Publishers", "handwritten", "->", o_p_h,
                                r_p_h,
                                recovered_architecture)
    o_p_h = set(n for n in observed_summary.subscribers if n[0] in hw_p)
    r_p_h = set(n for n in recovered_summary.subscribers if n[0] in hw_p)
    _, subcsv_hw = compare_sets("Subscribers", "handwritten", "<-", o_p_h,
                                r_p_h, recovered_architecture)
    o_p_h = set(n for n in observed_summary.providers if n[0] in hw_p)
    r_p_h = set(n for n in recovered_summary.providers if n[0] in hw_p)

    _, provcsv_hw = compare_sets("Providers", "handwritten", ":", o_p_h,
                                 r_p_h,
                                 recovered_architecture)
    o_p_h = set(n for n in observed_summary.action_clients if n[0] in hw_p)
    r_p_h = set(n for n in recovered_summary.action_clients if n[0] in hw_p)
    _, accsv_hw = compare_sets("Action Clients", "handwritten", "^-", o_p_h,
                               r_p_h, recovered_architecture)
    o_p_h = set(n for n in observed_summary.action_servers if n[0] in hw_p)
    r_p_h = set(n for n in recovered_summary.action_servers if n[0] in hw_p)
    _, ascsv_hw = compare_sets("Action Servers", "handwritten", "-^", o_p_h,
                               r_p_h, recovered_architecture)
    o_p_h = set(n for n in observed_summary.publishers if n[0] in re_p)
    r_p_h = set(n for n in recovered_summary.publishers if n[0] in re_p)
    _, pubcsv_re = compare_sets("Publishers", "recovered", "->", o_p_h,
                                r_p_h,
                                recovered_architecture)
    o_p_h = set(n for n in observed_summary.subscribers if n[0] in re_p)
    r_p_h = set(n for n in recovered_summary.subscribers if n[0] in re_p)
    _, subcsv_re = compare_sets("Subscribers", "recovered", "<-", o_p_h,
                                r_p_h, recovered_architecture)
    o_p_h = set(n for n in observed_summary.providers if n[0] in re_p)
    r_p_h = set(n for n in recovered_summary.providers if n[0] in re_p)

    _, provcsv_re = compare_sets("Providers", "recovered", ":", o_p_h,
                                 r_p_h,
                                 recovered_architecture)
    o_p_h = set(n for n in observed_summary.action_clients if n[0] in re_p)
    r_p_h = set(n for n in recovered_summary.action_clients if n[0] in re_p)
    _, accsv_re = compare_sets("Action Clients", "recovered", "^-", o_p_h,
                               r_p_h, recovered_architecture)
    o_p_h = set(n for n in observed_summary.action_servers if n[0] in re_p)
    r_p_h = set(n for n in recovered_summary.action_servers if n[0] in re_p)
    _, ascsv_re = compare_sets("Action Servers", "recovered", "-^", o_p_h,
                               r_p_h, recovered_architecture)

    with open(comparison_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Subject", "Case", "Kind", "# observed", "# recovered", "# obs ! rec", "rec ! obs",
                         "over_approx", "under_approx", "# errors observed", "# errors recovered", "overlap matches",
                         "#handwritten", "#recovered", "# placeholders"])
        for i in (nodecsv_all, pubcsv_all, subcsv_all, provcsv_all, accsv_all, ascsv_all,
                  pubcsv_hw, subcsv_hw, provcsv_hw, accsv_hw, ascsv_hw,
                  pubcsv_re, subcsv_re, provcsv_re, accsv_re, ascsv_re):
            line = [config['subject']]
            if i == nodecsv_all:
                if len(observed_errors) > len(recovered_errors):
                    same = len(observed_errors.intersection(recovered_errors)) == len(observed_errors) - len(
                        recovered_errors)
                else:
                    same = len(recovered_errors.intersection(observed_errors)) == len(recovered_errors) - len(
                        observed_errors)
                line += i
                line += [len(observed_errors), len(recovered_errors), same, len(handwritten),
                         len(recovered), len(placeholders)]
            else:
                line += i
            writer.writerow(line)
        for node in [node for node in recovered_architecture if node["provenance"] == "recovered"]:
            if ('ph', node["fullname"]) in observed_summary.nodes:
                o_p_h = set(n for n in observed_summary.publishers if n[0] == node["fullname"][1:])
                r_p_h = set(n for n in recovered_summary.publishers if n[0] == node["fullname"][1:])
                _, pubcsv_re = compare_sets("Publishers", "recovered", "->", o_p_h,
                                            r_p_h,
                                            recovered_architecture)
                o_p_h = set(n for n in observed_summary.subscribers if n[0] == node["fullname"][1:])
                r_p_h = set(n for n in recovered_summary.subscribers if n[0] == node["fullname"][1:])
                _, subcsv_re = compare_sets("Subscribers", "recovered", "<-", o_p_h,
                                            r_p_h, recovered_architecture)
                o_p_h = set(n for n in observed_summary.providers if n[0] == node["fullname"][1:])
                r_p_h = set(n for n in recovered_summary.providers if n[0] == node["fullname"][1:])

                _, provcsv_re = compare_sets("Providers", "recovered", ":", o_p_h,
                                             r_p_h,
                                             recovered_architecture)
                o_p_h = set(n for n in observed_summary.action_clients if n[0] == node["fullname"][1:])
                r_p_h = set(n for n in recovered_summary.action_clients if n[0] == node["fullname"][1:])
                _, accsv_re = compare_sets("Action Clients", "recovered", "^-", o_p_h,
                                           r_p_h, recovered_architecture)
                o_p_h = set(n for n in observed_summary.action_servers if n[0] == node["fullname"][1:])
                r_p_h = set(n for n in recovered_summary.action_servers if n[0] == node["fullname"][1:])
                _, ascsv_re = compare_sets("Action Servers", "recovered", "-^", o_p_h,
                                           r_p_h, recovered_architecture)
                for i in (pubcsv_re, subcsv_re, provcsv_re, accsv_re, ascsv_re):
                    line = [config['subject'], node['fullname']] + i
                    writer.writerow(line)

    with open(errors_both_csv, 'w') as f:
        writer = csv.writer(f)
        for i in observed_errors:
            writer.writerow([config['subject'], "observed", i])
        for i in recovered_errors:
            writer.writerow([config['subject'], "recovered", i])


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
        "system",
        help="the system to use for comparing architectures. "
             "(Note, assumed that observe and recover have been run)",
    )
    add_common_options(parser)
    args = parser.parse_args()

    config = load_config("recovery", args.system, args.experiment, args.results_dir)
    compare(config)


if __name__ == "__main__":
    main()
