#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import abc
import argparse
import contextlib
import csv
import json
import os
import sys
import tempfile
import typing as t
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from common.cli import add_common_options

logger.remove()

from rosdiscover.recover.call import SymbolicRosApiCall
from rosdiscover.recover.loader import SymbolicProgramLoader
from roswire.util import Stopwatch
import attr
import rosdiscover
import rosdiscover.cli
import yaml

from common.config import (
    configuration_to_experiment_file, NodeSources,
    RecoveryExperimentConfig,
    load_config
)


@attr.s(auto_attribs=True, slots=True)
class NodeModelRecoverySummary(abc.ABC):
    system: str
    package: str
    node: str
    entrypoint: str
    time_taken: float

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {
            "system": self.system,
            "package": self.package,
            "node": self.node,
            "entrypoint": self.entrypoint,
            "time_taken": self.time_taken,
        }


@attr.s(auto_attribs=True, slots=True)
class CrashedNodeModelRecoverySummary(NodeModelRecoverySummary):
    error_message: str

    def to_dict(self) -> t.Dict[str, t.Any]:
        dict_ = super().to_dict()
        dict_["crashed"] = True
        dict_["error_message"] = self.error_message
        return dict_


@attr.s(auto_attribs=True, slots=True)
class CompletedNodeModelRecoverySummary(NodeModelRecoverySummary):
    functions: int
    statements: int
    api_calls: int
    unknown_api_calls: int
    unreachable_functions: int
    unreachable_api_calls: int

    @classmethod
    def build(
        cls,
        experiment_config: RecoveryExperimentConfig,
        system: str,
        model_filename: str,
        time_taken: float,
    ) -> CompletedNodeModelRecoverySummary:
        # we need to load the rosdiscover config
        config_filename = experiment_config["config_with_node_sources_filename"]
        config = rosdiscover.Config.load(config_filename)

        # summarize model
        with open(model_filename, "r") as fh:
            model = json.load(fh)
            node = model["node-name"]
            package = model["package"]["name"]
            program = SymbolicProgramLoader.for_config(config).load(model["program"])
            entrypoint = program.entrypoint_name
            num_functions = len(program.functions)

            statements = []
            for function in program.functions.values():
                statements += list(function.body)
            num_statements = len(statements)

            # FIXME this is flawed: API calls may be nested inside a statement
            api_calls = [s for s in statements if isinstance(s, SymbolicRosApiCall)]
            num_api_calls = len(api_calls)

            unknown_api_calls = [c for c in api_calls if c.is_unknown()]
            num_unknown_api_calls = len(unknown_api_calls)

            num_unreachable_functions = len(program.unreachable_functions)
            unreachable_api_calls = []
            for function in program.unreachable_functions:
                unreachable_api_calls += [s for s in function.body if isinstance(s, SymbolicRosApiCall)]
            num_unreachable_api_calls = len(unreachable_api_calls)

        return CompletedNodeModelRecoverySummary(
            system=system,
            package=package,
            node=node,
            entrypoint=entrypoint,
            time_taken=time_taken,
            functions=num_functions,
            statements=num_statements,
            api_calls=num_api_calls,
            unknown_api_calls=num_unknown_api_calls,
            unreachable_functions=num_unreachable_functions,
            unreachable_api_calls=num_unreachable_api_calls,
        )

    def to_dict(self) -> t.Dict[str, t.Any]:
        dict_ = super().to_dict()
        dict_["crashed"] = False
        dict_["functions"] = self.functions
        dict_["statements"] = self.statements
        dict_["api_calls"] = self.api_calls
        dict_["unknown_api_calls"] = self.unknown_api_calls
        dict_["unreachable_api_calls"] = self.unreachable_api_calls
        dict_["unreachable_functions"] = self.unreachable_functions
        return dict_


@attr.s
class NodeModelRecoverySummaries:
    _summaries: t.List[NodeModelRecoverySummary] = attr.ib(factory=list)

    def add(self, summary: NodeModelRecoverySummary) -> None:
        self._summaries.append(summary)

    def save(self, filename: str) -> None:
        """Saves this collection of summaries to a CSV file."""
        with open(filename, "w") as fh:
            field_names = [
                "system",
                "package",
                "node",
                "entrypoint",
                "time_taken",
                "crashed",
                "error_message",
                "functions",
                "statements",
                "api_calls",
                "unknown_api_calls",
                "unreachable_functions",
                "unreachable_api_calls",
            ]
            writer = csv.DictWriter(fh, field_names)
            writer.writeheader()
            for summary in self._summaries:
                writer.writerow(summary.to_dict())


class RecoveryConfig(t.TypedDict):
    image: str
    sources: t.Sequence[str]
    # FIXME we need a set of launches to get the recovery command to work right now, which is a bit of a hack
    launches: t.Sequence[str]


@contextlib.contextmanager
def generate_temporary_recovery_config(
    experiment_config: RecoveryExperimentConfig,
) -> t.Iterator[str]:
    """Creates a temporary ROSDiscover config file for a given recovery experiment."""
    recovery_config: t.Dict[str, t.Any] = {
        "image": experiment_config["docker"]["image"],
        "sources": list(experiment_config["sources"]),
        "launches": list(experiment_config["launches"]),
    }

    try:
        recovery_config_filename: str = tempfile.mkstemp(suffix=".rosdiscover.yml")[1]
        with open(recovery_config_filename, "w") as fh:
            yaml.dump(recovery_config, fh, default_flow_style=False)

        yield recovery_config_filename

    finally:
        os.remove(recovery_config_filename)


def generate_node_sources(
    experiment_config: RecoveryExperimentConfig,
) -> None:
    """Generates a config file with node/nodelet sources information for a given experiment."""
    config_with_node_sources_filename = experiment_config["config_with_node_sources_filename"]
    with generate_temporary_recovery_config(experiment_config) as recovery_config_filename:
        args = [
            "sources",
            "--save-to",
            config_with_node_sources_filename,
            recovery_config_filename,
        ]
        logger.debug(f"calling rosdiscover: {args}")
        try:
            rosdiscover.cli.main(args)
        except Exception:
            logger.exception("failure occurred when recovering node sources")
            error(f"failed to obtain node sources for experiment [{experiment_config['filename']}]")


def obtain_node_sources(
    experiment_config: RecoveryExperimentConfig,
    should_cache: bool = True,
) -> t.Mapping[t.Tuple[str, str], NodeSources]:
    config_with_node_sources_filename = experiment_config["config_with_node_sources_filename"]
    results_directory = experiment_config["results_directory"]
    logs_directory = os.path.join(results_directory, "logs")
    os.makedirs(logs_directory, exist_ok=True)
    log_filename = os.path.join(logs_directory, f"obtain_node_sources.log")
    file_logger = logger.add(log_filename, level="DEBUG")
    try:
        if should_cache and os.path.exists(config_with_node_sources_filename):
            logger.debug("Using cached node sources")
        else:
            logger.debug("Obtaining all sources")
            generate_node_sources(experiment_config)
    finally:
        logger.remove(file_logger)

    with open(config_with_node_sources_filename, "r") as fh:
        dict_ = yaml.safe_load(fh)

    node_sources: t.Collection[NodeSources] = dict_["node_sources"]
    package_node_to_sources: t.Mapping[t.Tuple[str, str], NodeSources] = {
        (ns["package"], ns["node"]): ns for ns in node_sources
    }
    return package_node_to_sources


def do_recover(args) -> t.Optional[NodeModelRecoverySummary]:
    experiment_config, node_sources = args[0], args[1]
    return recover_node_from_sources(experiment_config, node_sources)


def recover_all(
    experiment_config: RecoveryExperimentConfig,
    should_cache_sources: bool,
    num_cores: int,
) -> None:
    logger.info("recovering all node models for system")
    summaries = NodeModelRecoverySummaries()
    package_node_to_sources = obtain_node_sources(
        experiment_config=experiment_config,
        should_cache=should_cache_sources,
    )

    # we need to load the rosdiscover config
    config_filename = experiment_config["config_with_node_sources_filename"]
    config = rosdiscover.Config.load(config_filename)

    # ensure that an app description is built before performing recovery
    config.app.describe()

    jobs = [(experiment_config, ns) for ns in package_node_to_sources.values()]

    with ThreadPoolExecutor(num_cores) as executor:
        for summary in executor.map(do_recover, jobs):
            if summary:
                summaries.add(summary)

    logger.info("recovered all node models for system")

    summary_filename = os.path.join(experiment_config["results_directory"], "recovered-models.csv")
    logger.info(f"writing summary to disk: {summary_filename}")
    summaries.save(summary_filename)
    logger.info("wrote summary to disk")


def recover_single_node(
    experiment_config: RecoveryExperimentConfig,
    package: str,
    node: str,
    should_cache_sources: bool,
) -> None:
    package_node_to_sources = obtain_node_sources(
        experiment_config=experiment_config,
        should_cache=should_cache_sources,
    )
    try:
        node_sources = package_node_to_sources[(package, node)]
    except KeyError:
        error(f"failed to find sources for node [{node}] in package [{package}]")
    recover_node_from_sources(experiment_config, node_sources)


def recover_node_from_sources(
    experiment_config: RecoveryExperimentConfig,
    node_sources: NodeSources,
) -> t.Optional[NodeModelRecoverySummary]:
    entrypoint = node_sources.get("entrypoint", "main")
    package = node_sources["package"]
    node = node_sources["node"]
    sources = node_sources["sources"]
    restrict_to_paths = node_sources["restrict-analysis-to-paths"]
    logger.info(f"statically recovering model for node [{node}] in package [{package}]")

    # ensure that a models output directory exists for this system
    experiment_directory = experiment_config["directory"]
    results_directory = experiment_config["results_directory"]
    # TODO: Should generated models go in results or with the experiment?
    models_directory = os.path.join(results_directory, "models")
    logs_directory = os.path.join(results_directory, "logs")
    os.makedirs(models_directory, exist_ok=True)
    os.makedirs(logs_directory, exist_ok=True)
    model_filename = os.path.join(models_directory, f"{package}__{node}.json")
    log_filename = os.path.join(logs_directory, f"{package}__{node}.log")

    with generate_temporary_recovery_config(experiment_config) as recovery_config_filename:
        args = [
            "recover",
            "--save-to",
            model_filename,
            "--entrypoint",
            entrypoint,
        ]
        for restrict_to in restrict_to_paths:
            args += ["--restrict-to", restrict_to]

        args += [
            recovery_config_filename,
            package,
            node,
        ]
        args += sources

        summary: NodeModelRecoverySummary
        file_logger = logger.add(log_filename, level="DEBUG")
        logger.debug(f"calling rosdiscover: {args}")
        timer = Stopwatch()
        timer.start()
        try:
            rosdiscover.cli.main(args)
            summary = CompletedNodeModelRecoverySummary.build(
                experiment_config=experiment_config,
                system=experiment_config["subject"],
                model_filename=model_filename,
                time_taken=timer.duration,
            )
            logger.info(f"statically recovered model for node [{node}] in package [{package}]: {summary}")
        except rosdiscover.recover.tool.CompileCommandsNotFound:
            logger.info(f"ignoring node without compile_commands.json: {node}")
            return None
        except Exception as err:
            summary = CrashedNodeModelRecoverySummary(
                system=experiment_config["subject"],
                package=package,
                node=node,
                entrypoint=entrypoint,
                time_taken=timer.duration,
                error_message=str(err),
            )
            logger.exception(f"failed to statically recover model for node [{node}] in package [{package}]")
        finally:
            logger.remove(file_logger)

        return summary


def error(message: str) -> t.NoReturn:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser("statically recovers node models")
    parser.add_argument(
        "system",
        help="the name of the system",
    )
    parser.add_argument(
        "--package",
        default=None,
        required=False,
        help="the name of the package containing the node whose model should be recovered",
    )
    parser.add_argument(
        "--node",
        default=None,
        required=False,
        help="the name of the node whose model should be recovered",
    )
    parser.add_argument(
        "--cores",
        type=int,
        default=1,
        help="the number of cores that the recovery process should be spread across",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enables verbose logging for debugging purposes",
    )
    parser.add_argument(
        "--no-cache-sources",
        action="store_false",
        dest="should_cache_sources",
        help="disables caching of node sources",
    )
    add_common_options(parser)
    args = parser.parse_args()

    # enable logging
    debug_level = "DEBUG" if args.debug else "INFO"
    stderr_logger = logger.add(
        sys.stderr,
        colorize=True,
        format="<bold><level>{level}:</level></bold> {message}",
        level=debug_level,
    )

    if args.node and not args.package:
        error(f"expected package name to be specified for node [{args.node}]")

    if args.package and not args.node:
        error(f"expected node name to be specified along with package [{args.package}]")

    # load experiment config
    config = load_config("recovery", args.system, args.experiment, args.results_dir)
    if config["type"] != "recovery":
        error(f"this script can only be run on recovery experiments")

    # determine if we should recover all models or just one
    should_recover_all = not args.node
    if should_recover_all:
        recover_all(
            experiment_config=config,
            should_cache_sources=args.should_cache_sources,
            num_cores=args.cores,
        )
    else:
        recover_single_node(
            experiment_config=config,
            package=args.package,
            node=args.node,
            should_cache_sources=args.should_cache_sources,
        )


if __name__ == "__main__":
    main()
