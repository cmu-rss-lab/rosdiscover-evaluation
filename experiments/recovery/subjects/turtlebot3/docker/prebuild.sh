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
sed -i 's/private_nh_.param("use_map_topic", use_map_topic_, false);/private_nh_.param("use_map_topic", use_map_topic_, true);/' /ros_ws/src/navigation/amcl/src/amcl_node.cpp
#sed -i 's/r.sleep();/\/\/r.sleep();/' /ros_ws/src/navigation/move_base/src/move_base.cpp
#sed -i 's/current_time.toSec() - global_pose.stamp_.toSec() > transform_tolerance_/false/' /ros_ws/src/navigation/costmap_2d/src/costmap_2d_ros.cpp
sed -i 's/if(as_->isNewGoalAvailable()){/if(as_->isNewGoalAvailable()){\nROS_WARN("[move_base] isNewGoalAvailable=true");/' /ros_ws/src/navigation/move_base/src/move_base.cpp
sed -i 's/if(as_->isPreemptRequested()){/if(as_->isPreemptRequested()){\nROS_WARN("[move_base] isPreemptRequested=true");/' /ros_ws/src/navigation/move_base/src/move_base.cpp
