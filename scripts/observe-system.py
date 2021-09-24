# -*- coding: utf-8 -*-
import argparse
import os
import sys
import typing as t

from loguru import logger

logger.remove()

import rosdiscover
import rosdiscover.cli

from common.config import (
    ExperimentConfig,
    RecoveryExperimentConfig,
    ROSDiscoverConfig,
    load_config
)

from common import generate_and_check_acme


def observe(config: ExperimentConfig) -> None:
    ({
        "detection": _error_not_supported,
        "recovery": _observe_for_recovery_experiment,
    })[config["type"]](config)


def _error_not_supported(config: RecoveryExperimentConfig) -> None:
    error(f"{config['type']} not supported for dynamic recovery")


def _observe_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    config_directory = config["directory"]
    log_directory = os.path.join(config_directory, "logs")
    output_filename = os.path.join(config_directory, "observed.architecture.yml")
    log_filename = os.path.join(log_directory, "system-recovery.log")
    observe_system(
        image=config["image"],
        sources=config["sources"],
        environment=config["environment"],
        launches=config["launches"],
        output_filename=output_filename,
        log_filename=log_filename,
    )

    acme_filename = os.path.join(config_directory, "observed.archiecture.acme")
    acme_log_filename = os.path.join(log_directory, "acme-and-check-observed.log")
    generate_and_check_acme(
        image=config["image"],
        input_filename=output_filename,
        output_filename=acme_filename,
        log_filename=acme_log_filename,
    )


def observe_system(
    image: str,
    sources: t.Sequence[str],
    environment: t.Mapping[str, str],
    launches: t.Sequence[str],  # FIXME
    output_filename: str,
    log_filename: str,
) -> None:
    # ensure that the logs directory exists
    os.makedirs(os.path.dirname(log_filename), exists_ok=True)

    # Add in display variable for the gazebo client
    embellished_environment = dict(environment)
    embellished_environment["DISPLAY"] = ":1.0"

    with ROSDiscoverConfig.create_temporary({
        "image": image,
        "sources": list(sources),
        "launches": list(launches),
        "environment": embellished_environment,
    }) as config_filename:
        args = ["observe", config_filename]
        args += ["--output", output_filename]
        args += ["--duration",  "30",  "--interval", "10",
                 "--do-launch",  "--launch-sleep", "30"]
        file_logger = logger.add(log_filename, level="DEBUG")
        try:
            rosdiscover.cli.main(args)
        except Exception:
            logger.exception(f"failed to statically recover system architecture for image [{image}]")
        finally:
            logger.remove(file_logger)
        logger.info(f"dynamically recovered system architecture for image [{image}]")


def error(message: str) -> t.NoReturn:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    # remove all existing loggers
    stderr_logger = logger.add(
        sys.stderr,
        colorize=True,
        format="<bold><level>{level}:</level></bold> {message}",
        level="INFO",
    )

    parser = argparse.ArgumentParser("dynamically recovers ROS system architectures")
    parser.add_argument(
        "configuration",
        help="the path to the configuration file for this experiment",
    )
    args = parser.parse_args()

    experiment_filename: str = args.configuration
    if not os.path.exists(experiment_filename):
        error(f"configuration file not found: {experiment_filename}")

    config = load_config(experiment_filename)
    observe(config)


if __name__ == "__main__":
    main()
