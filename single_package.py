import sys
from pathlib import Path
import get_packages as gp
import xml.etree.ElementTree as ET
import os
import yaml
from yaml.loader import SafeLoader

from pathlib import Path


from git import *
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
