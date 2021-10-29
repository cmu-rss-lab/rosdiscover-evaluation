# -*- coding: utf-8 -*-
import os
import tempfile

from loguru import logger

import rosdiscover
import rosdiscover.cli

from .config import ROSDiscoverConfig


THINGS_TO_IGNORE = """/clock
/tf
/tf_static
/diagnostics
*/load_nodelet
*/unload_nodelet
*/bond
*/list_controllers
*/parameter_descriptions
*/parameter_description
*/parameter_updates
*/set_parameters
"""


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
        ignore_file: str = tempfile.mkstemp(suffix="ignore.txt")[1]
        with open(ignore_file, 'w') as fh:
            fh.write(THINGS_TO_IGNORE)

        args = ["acme", config_filename]
        args += ["--from-yml", input_filename]
        args += ["--acme", output_filename]
        args += ["--check"]
        args += ["--ignore-list", ignore_file]
        file_logger = logger.add(log_filename, level="DEBUG")
        logger.debug(f"Calling rosdiscover: {args}")
        try:
            rosdiscover.cli.main(args)
        except Exception:
            logger.exception(f"Failed to convert yml file to Acme for [{image}] captured in [{input_filename}]")
        finally:
            if ignore_file:
                os.remove(ignore_file)
            logger.remove(file_logger)

