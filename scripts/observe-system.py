#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import typing as t

from loguru import logger

from common.cli import add_common_options

logger.remove()

import rosdiscover
import rosdiscover.cli

from common.config import (
    configuration_to_experiment_file, ExperimentConfig,
    RecoveryExperimentConfig,
    ROSDiscoverConfig,
    load_config
)


def observe(config: ExperimentConfig) -> None:
    ({
        "detection": _error_not_supported,
        "recovery": _observe_for_recovery_experiment,
    })[config["type"]](config)


def _error_not_supported(config: RecoveryExperimentConfig) -> None:
    error(f"{config['type']} not supported for dynamic recovery")


def _observe_for_recovery_experiment(config: RecoveryExperimentConfig) -> None:
    config_directory = config["directory"]
    results_directory = config["results_directory"]
    log_directory = os.path.join(results_directory, "logs")
    output_filename = os.path.join(results_directory, "observed.architecture.yml")
    log_filename = os.path.join(log_directory, "system-observed.log")
    run_script_filename = None
    if "run_script" in config and config["run_script"] is not None:
        run_script_filename = os.path.join(results_directory, "run.while.observing.sh")
        with open(run_script_filename, 'w') as f:
            f.write("#!/bin/bash\n")
            for source in config["sources"]:
                f.write(f"source {source}\n")
            for var, val in config["environment"].items():
                f.write(f"export {var}={val}\n")
            f.write(config["run_script"] + "\n")

    observe_system(
        image=config["docker"]["image"],
        sources=config["sources"],
        environment=config["environment"],
        launches=config["launches"],
        output_filename=output_filename,
        log_filename=log_filename,
        run_filename=run_script_filename,
    )




def observe_system(
    image: str,
    sources: t.Sequence[str],
    environment: t.Mapping[str, str],
    launches: t.Sequence[str],  # FIXME
    output_filename: str,
    log_filename: str,
    run_filename: t.Optional[str]
) -> None:
    # ensure that the logs directory exists
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

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
        args += ["--duration",  "600",  "--interval", "30",
                 "--do-launch",  "--launch-sleep", "30"]
        if run_filename is not None:
            args += ["--run-script", run_filename]
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
        "system",
        help="the system to observe",
    )
    add_common_options(parser)
    args = parser.parse_args()

    config = load_config("recovery", args.system, args.experiment, args.results_dir)
    observe(config)


if __name__ == "__main__":
    main()
