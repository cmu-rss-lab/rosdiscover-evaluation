# -*- coding: utf-8 -*-
import os


def main():
    print("Available experiments and systems:")
    for experiment in ("detection", "recovery"):
        print(f"  Systems under '{experiment}':\n")
        subject_dir = os.path.join(os.path.dirname(__file__), '../experiments', experiment, 'subjects')
        for directory in os.listdir(subject_dir):
            if os.path.isdir(os.path.join(subject_dir, experiment)) and \
               os.path.isfile(os.path.join(subject_dir, experiment, "experiment.yml")):
                print(f"    {directory}\n")


if __name__ == "__main__":
    main()
