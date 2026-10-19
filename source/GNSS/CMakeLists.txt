cmake_minimum_required(VERSION 3.0.2)
project(gnss_waypoint_navigation)
find_package(catkin REQUIRED COMPONENTS
  rospy actionlib actionlib_msgs sensor_msgs move_base_msgs
  geographic_msgs robot_localization tf
)
catkin_package()
catkin_install_python(PROGRAMS
  scripts/gnss_waypoint_nav.py
  scripts/preview_waypoints.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
install(DIRECTORY config launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
