# -*- coding: utf-8 -*-
import os


def main():
    print("Available experiments and systems:")
    for experiment in ("detection", "recovery"):
        print(f"  Systems under '{experiment}':")
        subject_dir = os.path.join(os.path.dirname(__file__), '../experiments', experiment, 'subjects')
        for directory in os.listdir(subject_dir):
            isdir = os.path.isdir(os.path.join(subject_dir, directory))
            contains_experiment_yml = os.path.isfile(os.path.join(subject_dir, directory, "experiment.yml"))
            if isdir and contains_experiment_yml:
                print(f"    {directory}")


if __name__ == "__main__":
    main()
