import sys
from pathlib import Path
import get_packages as gp
import xml.etree.ElementTree as ET
import os
import yaml
from pathlib import Path

from git import Git
from git import Repo

THIS_DIR = os.path.dirname(__file__)
rgtm_dir = os.path.join(THIS_DIR, "rosinstall_generator_time_machine")
tempdir = os.path.join(THIS_DIR, "ros-temp")
 

with open(sys.argv[1] + "/bug.yml") as f:
    data = yaml.safe_load(f)

docker_dir = sys.argv[2]

repo_url = data["repo-url"]
repo_name = data["repo-name"]
pre_bug_commit = data["pre-bug-commit"]
bug_commit = data["bug-commit"]
bug_fix_commit = data["bug-fix-commit"]
bug_id = data["bugid"]
localReposPath = os.path.join(tempdir,"repos")
relative_out_dir = os.path.join("ros-temp", bug_id, "time")
out_dir = os.path.join(tempdir, bug_id, "time")
distro = data["ros-distro"]
additional_packages = data["additional-packages"] if "additional-packages" in data else ""
apt_get_packages = data["apt-get-packages"] if "apt-get-packages" in data else "" 

if not os.path.exists(out_dir):
    Path(out_dir).mkdir(parents=True)
if not os.path.exists(localReposPath):
    Path(localReposPath).mkdir(parents=True)

localRepoPath = os.path.join(localReposPath, repo_name)
if not os.path.exists(localRepoPath):
    print("Cloning repo into " + localRepoPath)
    p = Git(localReposPath).clone(repo_url)
    print("Done cloning repo")
g = Git(localRepoPath)
r = Repo(localRepoPath)
repoUrl = r.remotes[0].url

if not os.path.exists(os.path.join(out_dir,"pre_bug.rosinstall")):
    c = r.commit(pre_bug_commit)
    c_date = c.authored_datetime.isoformat()
    g.checkout(pre_bug_commit)
    for submodule in r.submodules:
        submodule.update(init=True, recursive=True)
    neededPackages = gp.get_packages(localRepoPath)
    pc = ' '.join(neededPackages) + " " + additional_packages
    command = "yes | "+rgtm_dir+"/rosinstall_generator_tm.sh '"+c_date+"' "+distro+" "+pc+" --deps --tar | sed -e 's/geometry_experimental-release/geometry2-release/g' > "+out_dir+"/pre_bug.rosinstall"
    os.system(command)
    file1 = open(out_dir+"/pre_bug.rosinstall", "a")  # append mode
    file1.write("- git:\n    local-name: repo\n    uri:  "+repoUrl+"\n    version: "+pre_bug_commit)
    file1.close()

if not os.path.exists(os.path.join(out_dir,"bug.rosinstall")):
    c = r.commit(bug_commit)
    c_date = c.authored_datetime.isoformat()
    g.checkout(bug_commit)
    for submodule in r.submodules:
        submodule.update(init=True, recursive=True)
    neededPackages = gp.get_packages(localRepoPath)
    pc = ' '.join(neededPackages) + " " + additional_packages
    command = "yes | "+ os.path.join(rgtm_dir,"rosinstall_generator_tm.sh '") +c_date+"' "+distro+" "+pc+" --deps --tar | sed -e 's/geometry_experimental-release/geometry2-release/g' > "+out_dir+"/bug.rosinstall"
    print(command)
    os.system(command)
    with open(out_dir+"/bug.rosinstall", "a") as file2: # append mode
        file2.write("- git:\n    local-name: repo\n    uri:  "+repoUrl+"\n    version: "+bug_commit)

if not os.path.exists(os.path.join(out_dir,"bug_fix.rosinstall")):
    c = r.commit(bug_fix_commit)
    c_date = c.authored_datetime.isoformat()
    g.checkout(bug_fix_commit)
    for submodule in r.submodules:
        submodule.update(init=True)
    neededPackages = gp.get_packages(localRepoPath)
    pc = ' '.join(neededPackages) + " " + additional_packages
    command = "yes | "+rgtm_dir+"/rosinstall_generator_tm.sh '"+c_date+"' "+distro+" "+pc+" --deps --tar | sed -e 's/geometry_experimental-release/geometry2-release/g' > "+out_dir+"/bug_fix.rosinstall"
    os.system(command)
    file3 = open(out_dir+"/bug_fix.rosinstall", "a")  # append mode
    file3.write("- git:\n    local-name: repo\n    uri:  "+repoUrl+"\n    version: "+bug_fix_commit)
    file3.close()


print(docker_dir)
if docker_dir != 'none':

    dockerCmd = "docker build . -t "+ bug_id + " --build-arg APT_GET_PACKAGES='"+apt_get_packages+"' --build-arg ROOTFS='./"+sys.argv[1]+"/rootfs/' --build-arg DISTRO="+distro+" --build-arg DIRECTORY="+relative_out_dir+" -f "+docker_dir
    print(dockerCmd)
    res = os.system(dockerCmd)