#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import os
import sys
import xml.etree.ElementTree as ET

from git import *
import yaml


def get_packages(repo):
    print(repo)

    definedPackages = set()
    usedPackages = set()
    for path in Path(repo).rglob('package.xml'):
        mytree = ET.parse(str(path))
        myroot = mytree.getroot()
        for x in myroot.findall('name'):
            definedPackages.add(x.text)
        for x in myroot.findall('build_depend'):
            usedPackages.add(x.text)
        for x in myroot.findall('build_export_depend'):
            usedPackages.add(x.text)
        for x in myroot.findall('depend'):
            usedPackages.add(x.text)
        for x in myroot.findall('run_depend'):
            usedPackages.add(x.text)

    neededPackages = usedPackages - definedPackages
    return neededPackages


def main() -> None:
    rgtm_dir = "./rosinstall_generator_time_machine"
    tempdir = "./ros-temp/"

    localRepoPath = sys.argv[1]
    commit = sys.argv[2]
    distro = sys.argv[3]
    package = sys.argv[4]

    g = Git(localRepoPath)
    r = Repo(localRepoPath)

    c = r.commit(commit)
    c_date = c.authored_datetime.isoformat()
    command = "yes | "+rgtm_dir+"/rosinstall_generator_tm.sh '"+c_date+"' "+distro+" "+package 
    os.system(command)


if __name__ == "__main__":
    main()
