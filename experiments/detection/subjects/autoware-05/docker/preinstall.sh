curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | python2.7

mkdir -p /etc/ros/rosdep/custom
cp /.dockerinstall/customrule.yaml /etc/ros/rosdep/custom/
echo "yaml file:///etc/ros/rosdep/custom/customrule.yaml" | sudo tee -a /etc/ros/rosdep/sources.list.d/50-custom.list
rosdep update
