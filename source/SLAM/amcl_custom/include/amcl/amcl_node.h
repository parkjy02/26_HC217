/*
 *  amcl_node.h
 *
 *  Copyright (c) 2008, Willow Garage, Inc.
 *  All rights reserved.
 */

#ifndef AMCL_AMCL_NODE_H
#define AMCL_AMCL_NODE_H

// C++ headers
#include <vector>
#include <map>
#include <string>
#include <memory>

#include <boost/thread/mutex.hpp>
#include <boost/thread/recursive_mutex.hpp>

// ROS headers
#include <ros/ros.h>
#include <ros/time.h>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>
#include <tf2_ros/message_filter.h>
#include <message_filters/subscriber.h>
#include <dynamic_reconfigure/server.h>
#include <diagnostic_updater/diagnostic_updater.h>

// ROS messages/services
#include <sensor_msgs/LaserScan.h>
#include <geometry_msgs/PoseWithCovarianceStamped.h>
#include <geometry_msgs/PoseArray.h>
#include <geometry_msgs/Pose.h>
#include <geometry_msgs/PoseStamped.h>
#include <nav_msgs/GetMap.h>
#include <nav_msgs/SetMap.h>
#include <nav_msgs/OccupancyGrid.h>
#include <std_srvs/Empty.h>

// AMCL includes
#include "amcl/map/map.h"
#include "amcl/pf/pf.h"
#include "amcl/sensors/amcl_odom.h"
#include "amcl/sensors/amcl_laser.h"
#include "amcl/AMCLConfig.h"

namespace amcl
{

#define NEW_UNIFORM_SAMPLING 1

typedef struct
{
  double weight;
  pf_vector_t pf_pose_mean;
  pf_matrix_t pf_pose_cov;
} amcl_hyp_t;

class AmclNode
{
public:
  AmclNode();
  ~AmclNode();

  void runFromBag(const std::string &in_bag_fn, bool trigger_global_localization = false);

  int process();
  void savePoseToServer();

private:
  // TF
  std::shared_ptr<tf2_ros::TransformBroadcaster> tfb_;
  std::shared_ptr<tf2_ros::TransformListener> tfl_;
  std::shared_ptr<tf2_ros::Buffer> tf_;

  bool sent_first_transform_;

  tf2::Transform latest_tf_;
  bool latest_tf_valid_;

  // Particle filter pose generators
  static pf_vector_t uniformPoseGenerator(void* arg);
  static pf_vector_t gaussianPoseGenerator(void* arg);

#if NEW_UNIFORM_SAMPLING
  static std::vector<std::pair<int, int> > free_space_indices;
#endif

  // Callbacks
  bool globalLocalizationCallback(std_srvs::Empty::Request& req, std_srvs::Empty::Response& res);
  bool nomotionUpdateCallback(std_srvs::Empty::Request& req, std_srvs::Empty::Response& res);
  bool setMapCallback(nav_msgs::SetMap::Request& req, nav_msgs::SetMap::Response& res);

  void laserReceived(const sensor_msgs::LaserScanConstPtr& laser_scan);
  void initialPoseReceived(const geometry_msgs::PoseWithCovarianceStampedConstPtr& msg);
  void handleInitialPoseMessage(const geometry_msgs::PoseWithCovarianceStamped& msg);
  void mapReceived(const nav_msgs::OccupancyGridConstPtr& msg);

  void handleMapMessage(const nav_msgs::OccupancyGrid& msg);
  void freeMapDependentMemory();
  map_t* convertMap(const nav_msgs::OccupancyGrid& map_msg);
  void updatePoseFromServer();
  void applyInitialPose();

  // Frame IDs and parameters
  std::string odom_frame_id_;
  geometry_msgs::PoseStamped latest_odom_pose_;
  std::string base_frame_id_;
  std::string global_frame_id_;

  bool use_map_topic_;
  bool first_map_only_;

  ros::Duration gui_publish_period;
  ros::Time save_pose_last_time;
  ros::Duration save_pose_period;
  geometry_msgs::PoseWithCovarianceStamped last_published_pose;

  // Map
  map_t* map_;
  char* mapdata;
  int sx, sy;
  double resolution;

  message_filters::Subscriber<sensor_msgs::LaserScan>* laser_scan_sub_;
  tf2_ros::MessageFilter<sensor_msgs::LaserScan>* laser_scan_filter_;
  ros::Subscriber initial_pose_sub_;
  std::vector<AMCLLaser*> lasers_;
  std::vector<bool> lasers_update_;
  std::map<std::string, int> frame_to_laser_;

  // Particle filter
  pf_t *pf_;
  double pf_err_, pf_z_;
  bool pf_init_;
  pf_vector_t pf_odom_pose_;
  double d_thresh_, a_thresh_;
  int resample_interval_;
  int resample_count_;
  double laser_min_range_;
  double laser_max_range_;

  bool m_force_update;

  AMCLOdom* odom_;
  AMCLLaser* laser_;

  ros::Duration cloud_pub_interval;
  ros::Time last_cloud_pub_time;
  ros::WallDuration bag_scan_period_;

  void requestMap();

  bool getOdomPose(geometry_msgs::PoseStamped& pose, double& x, double& y, double& yaw, const ros::Time& t, const std::string& f);

  ros::Duration transform_tolerance_;

  ros::NodeHandle nh_;
  ros::NodeHandle private_nh_;
  ros::Publisher pose_pub_;
  ros::Publisher particlecloud_pub_;
  ros::ServiceServer global_loc_srv_;
  ros::ServiceServer nomotion_update_srv_;
  ros::ServiceServer set_map_srv_;
  ros::Subscriber initial_pose_sub_old_;
  ros::Subscriber map_sub_;

  diagnostic_updater::Updater diagnosic_updater_;
  void standardDeviationDiagnostics(diagnostic_updater::DiagnosticStatusWrapper& diagnostic_status);
  double std_warn_level_x_;
  double std_warn_level_y_;
  double std_warn_level_yaw_;

  amcl_hyp_t* initial_pose_hyp_;
  bool first_map_received_;
  bool first_reconfigure_call_;

  boost::recursive_mutex configuration_mutex_;
  dynamic_reconfigure::Server<amcl::AMCLConfig> *dsrv_;
  amcl::AMCLConfig default_config_;
  ros::Timer check_laser_timer_;

  int max_beams_, min_particles_, max_particles_;
  double alpha1_, alpha2_, alpha3_, alpha4_, alpha5_;
  double alpha_slow_, alpha_fast_;
  double z_hit_, z_short_, z_max_, z_rand_, sigma_hit_, lambda_short_;
  // beam skip related params
  bool do_beamskip_;
  double beam_skip_distance_, beam_skip_threshold_, beam_skip_error_threshold_;
  double laser_likelihood_max_dist_;
  odom_model_t odom_model_type_;
  double init_pose_[3];
  double init_cov_[3];
  laser_model_t laser_model_type_;
  bool tf_broadcast_;
  bool selective_resampling_;

  void reconfigureCB(amcl::AMCLConfig &config, uint32_t level);

  ros::Time last_laser_received_ts_;
  ros::Duration laser_check_interval_;
  void checkLaserReceived(const ros::TimerEvent& event);
};

} // namespace amcl

#endif // AMCL_AMCL_NODE_H

