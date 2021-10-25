#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import csv
import os
import sys
import typing as t

import yaml
from loguru import logger
from rosdiscover.interpreter import SystemSummary

logger.remove()

from common import generate_and_check_acme
from common.config import (
    DetectionExperimentConfig,
    ExperimentConfig,
    RecoveryExperimentConfig,
    load_config,
)


def check(config: ExperimentConfig) -> None:
    ({
        "detection": _check_for_detection_experiment,
        "recovery": _check_for_recovery_experiment,
    })[config["type"]](config)


def _check_for_detection_experiment(config: DetectionExperimentConfig) -> None:
    error(f"{config['type']} not yet supported for detection experiment")


def _check_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    config_directory = config["directory"]
    log_directory = os.path.join(config_directory, "logs")
    input_filename = os.path.join(config_directory, "observed.architecture.yml")

    acme_filename = os.path.join(config_directory, "observed.architecture.acme")
    acme_log_filename = os.path.join(log_directory, "acme-and-check-observed.log")
    generate_and_check_acme(
        image=config["image"],
        input_filename=input_filename,
        output_filename=acme_filename,
        log_filename=acme_log_filename,
    )

    process_error_data(config['subject'], "Observed", input_filename, acme_log_filename, config_directory)


def process_error_data(subject: str,
                       case: str,
                       arch_yml_filename: str,
                       acme_check_log_filename: str,
                       results_dir: str):
    with open(arch_yml_filename, 'r') as f:
        arch = yaml.load(f, Loader=yaml.SafeLoader)
    assert isinstance(arch, list), type(arch)
    summary = SystemSummary.from_dict(arch)
    topics = set()
    services = set()
    actions = set()

    for node in summary.values():
        for t in node.pubs:
            topics.add(t)
        for t in node.subs:
            topics.add(t)
        for s in node.provides:
            services.add(s)
        for s in node.uses:
            services.add(s)
        for a in node.action_clients:
            actions.add(a)
        for a in node.action_servers:
            actions.add(a)

    errors = []
    with open(acme_check_log_filename, 'r') as f:
        lines = f.readlines()
        # errors reside on final lines of the log, so iterate through those until "The following problem.."
        # is detected
        line = len(lines) - 1
        while line > 0 and \
            not ("The following problems were found" in lines[line] or
                 "Robot architecture has no errors" in lines[line]):
            errors.insert(0, lines[line])
            line = line - 1

    with open(os.path.join(results_dir, 'system.observed.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Subject", "Case", "#Nodes", "#Topics", "#Services", "#Actions", "#Errors"])
        writer.writerow([subject, case, len(arch), len(topics), len(services), len(actions), len(errors)])

    with open(os.path.join(results_dir, 'observed.errors.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Node", "Error"])
        for e in errors:
            err = e.split('|')[2].split('- ')[1].strip()
            node = err.split()[0]
            writer.writerow([node, err])


def error(message: str) -> t.NoReturn:
    print(f"ERROR: {message}")
    sys.exit(1)


def main():
    # remove all existing loggers
    stderr_logger = logger.add(
        sys.stderr,
        colorize=True,
        format="<bold><level>{level}:</level></bold> {message}",
        level="INFO",
    )
    parser = argparse.ArgumentParser("Checks the architecture by converting to Acme and checking constraints")
    parser.add_argument(
        "configuration",
        help="the path to the configuration file for this experiment",
    )
    args = parser.parse_args()

    experiment_filename: str = args.configuration
    if not os.path.exists(experiment_filename):
        error(f"configuration file not found: {experiment_filename}")
    config = load_config(experiment_filename)

    check(config)


if __name__ == "__main__":
    main()
