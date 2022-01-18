#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import csv
import os
import sys
import typing as t

from loguru import logger

from common.acme import get_acme_errors
from common.cli import add_common_options

logger.remove()

from common import generate_and_check_acme
from common.config import (
    configuration_to_experiment_file, DetectionExperimentConfig,
    ExperimentConfig,
    RecoveryExperimentConfig,
    load_config,
)


def check(config: ExperimentConfig, kind: str) -> None:
    ({
        "detection": _check_for_detection_experiment,
        "recovery": _check_for_recovery_experiment,
    })[config["type"]](config, kind)


def _check_for_detection_experiment(config: DetectionExperimentConfig, kind: str) -> None:
    config_directory = config["directory"]
    results_directory = config["results_directory"]
    log_directory = os.path.join(results_directory, "logs")
    detection_report_csv = os.path.join(results_directory, "error-report.csv")

    for kind in ("buggy", "fixed"):
        input_filename = os.path.join(results_directory, f"{kind}.architecture.yml")
        acme_filename = os.path.join(results_directory, f"{kind}.architecture.acme")
        acme_log_filename = os.path.join(log_directory, f"acme-and-check-{kind}.log")
        generate_and_check_acme(
            image=config[kind]["docker"]["image"],
            input_filename=input_filename,
            output_filename=acme_filename,
            log_filename=acme_log_filename,
        )

    errors_required = config["errors"]
    errors_detected_buggy = get_acme_errors(os.path.join(log_directory, f"acme-and-check-buggy.log"))
    found_in_buggy = []
    for err in errors_required:
        detected = [e for e in errors_detected_buggy if err in e]
        found_in_buggy.append((err, detected))
    errors_detected_fixed = get_acme_errors(os.path.join(log_directory, f"acme-and-check-fixed.log"))
    found_in_fixed = []
    for err in errors_required:
        detected = [e for e in errors_detected_fixed if err in e]
        found_in_fixed.append((err, detected))

    def error_messages(errors):
        ret = []
        for v, err in errors:
            for e in err:
                ret.append(e)
        return ret

    with open(detection_report_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow([config["subject"], "", "", "", len(errors_detected_buggy), len(errors_detected_fixed),
                         len(errors_required), len(error_messages(found_in_buggy)),
                         len(error_messages(found_in_fixed))])
        for err in found_in_buggy:
            for errMsg in err[1]:
                writer.writerow([config["subject"], "buggy", err[0], errMsg.strip()])
        if len(error_messages(found_in_buggy)) == 0:
            writer.writerow([config["subject"], "buggy", "-", "NO RELEVANT ERROR DETECTED"])
        for err in found_in_fixed:
            for errMsg in err[1]:
                writer.writerow([config["subject"], "fixed", err[0], errMsg.strip()])
        if len(error_messages(found_in_fixed)) == 0:
            writer.writerow([config["subject"], "fixed", "-", "NO RELEVANT ERROR DETECTED"])


def _check_for_recovery_experiment(config: RecoveryExperimentConfig, kind: str) -> None:
    config_directory = config["directory"]
    results_directory = config["results_directory"]
    log_directory = os.path.join(results_directory, "logs")
    input_filename = os.path.join(results_directory, f"{kind}.architecture.yml")

    acme_filename = os.path.join(results_directory, f"{kind}.architecture.acme")
    acme_log_filename = os.path.join(results_directory, f"acme-and-check-{kind}.txt")
    generate_and_check_acme(
        image=config["docker"]["image"],
        input_filename=input_filename,
        output_filename=acme_filename,
        log_filename=acme_log_filename,
    )


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
    parser.add_argument('kind', type=str, choices=['observed', 'recovered', 'detected'])
    parser.add_argument(
        "configuration",
        help="the path to the configuration file for this experiment",
    )

    add_common_options(parser)
    args = parser.parse_args()
    experiment_dir = "detection" if args.kind == 'detected' else 'recovery'

    config = load_config(experiment_dir, args.configuration, args.experiment, args.results_dir)

    check(config, args.kind)


if __name__ == "__main__":
    main()
