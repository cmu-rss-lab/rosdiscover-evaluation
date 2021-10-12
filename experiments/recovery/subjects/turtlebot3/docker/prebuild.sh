# # ensure that the python environment is correctly configured
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
# eval "$(pyenv virtualenv-init -)"

## install necessary python packages
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  defusedxml==0.6.0 \
  netifaces==0.10.7

sed -i 's/while(!ros::service::call("static_map", req, resp))/ros::Publisher service_pub_ = nh_.advertise<nav_msgs::GetMap::Request>("static_map", 2, true);\nfor(service_pub_.publish(req); !ros::service::call("static_map", req, resp); service_pub_.publish(req))/' /ros_ws/src/navigation/amcl/src/amcl_node.cpp
