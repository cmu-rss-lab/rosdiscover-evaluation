# -*- coding: utf-8 -*-
import os

from loguru import logger

import rosdiscover
import rosdiscover.cli

from .config import ROSDiscoverConfig


def generate_and_check_acme(
    image: str,
    input_filename: str,
    output_filename: str,
    log_filename: str,
) -> None:
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    with ROSDiscoverConfig.create_temporary({
        "image": image,
    }) as config_filename:
        args = ["acme", config_filename]
        args += ["--from-yml", input_filename]
        args += ["--acme", output_filename]
        args += ["--check"]
        file_logger = logger.add(log_filename, level="DEBUG")
        logger.debug(f"Calling rosdiscover: {args}")
        try:
            rosdiscover.cli.main(args)
        except Exception:
            logger.exception(f"Failed to convert yml file to Acme for [{image}] captured in [{input_filename}]")
        finally:
            logger.remove(file_logger)

