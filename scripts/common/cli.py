# -*- coding: utf-8 -*-
import argparse


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '-e', '--experiment', type=str, help='The experiment.yml to use', default='experiment.yml'
    )
    parser.add_argument(
        '-r', '--results_dir', type=str, default='results', help='The directory (relative to the repo) to store results'
    )
