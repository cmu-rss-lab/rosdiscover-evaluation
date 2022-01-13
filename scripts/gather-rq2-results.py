# -*- coding: utf-8 -*-
import typing as t
import csv
import os

from common.config import EVALUATION_DIR

RECOVERY_DIR = 'results/recovery/subjects/'
JUPYTER_RESULTS = 'results/data'


def get_comparison_file(system: str) -> str:
    return os.path.join(EVALUATION_DIR, RECOVERY_DIR, system, 'observed.recovered.compare.csv')


def main():
    rq2_systems = [system for system in os.listdir(RECOVERY_DIR) if os.path.isfile(get_comparison_file(system))]
    header = {}
    rq2_compares: t.Dict[str, t.List[t.Dict[str, str]]] = {}
    for system in rq2_systems:
        rq2_compares[system] = []
        with open(get_comparison_file(system), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rq2_compares[system].append(row)
                header = row.keys()

    # RQ2 Observed Architecture - Comparison
    with open(f"{JUPYTER_RESULTS}/RQ2 Observed Architecture - Comparison.csv", 'w') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for system, dicts in rq2_compares.items():
            for dict_ in [d for d in dicts if d["Case"] in {"all", "handwritten", "recovered"}]:
                writer.writerow(dict_)

    # RQ2 Observed Architecture -Node-Level Comparison
    with open(f"{JUPYTER_RESULTS}/RQ2 Observed Architecture - Node-Level Comparison.csv", 'w') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for system, dicts in rq2_compares.items():
            for dict_ in [d for d in dicts if d["Case"] not in {"all", "handwritten", "recovered"}]:
                writer.writerow(dict_)


if __name__ == "__main__":
    main()
