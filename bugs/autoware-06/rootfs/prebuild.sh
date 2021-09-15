git config --global user.email "you@example.com"
git config --global user.name "Your Name"
cd /pre_bug/src/repo/ros
git cherry-pick f504f37fb5e4ea7152b0101e155231ab6d2a9011
cd /bug/src/repo/ros
git cherry-pick f504f37fb5e4ea7152b0101e155231ab6d2a9011
cd /bug_fix/src/repo/ros
git cherry-pick f504f37fb5e4ea7152b0101e155231ab6d2a9011
