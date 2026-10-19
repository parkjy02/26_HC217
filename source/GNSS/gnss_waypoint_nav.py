#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ROS Noetic: GNSS(latitude/longitude) waypoints -> map-frame move_base goals.

This node does not localize the robot by itself. Real navigation requires a
working nmea_navsat_driver, robot_localization/navsat_transform_node, a correctly
georeferenced map/odom estimate, and a ready move_base navigation stack.
"""

import math
import os

import actionlib
import rospy
import yaml
from actionlib_msgs.msg import GoalStatus
from geographic_msgs.msg import GeoPoint
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from robot_localization.srv import FromLL
from sensor_msgs.msg import NavSatFix, NavSatStatus
from tf.transformations import quaternion_from_euler


DEFAULT_FILE = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "config", "waypoints.yaml"))


class GNSSWaypointNavigator:
    def __init__(self):
        self.file_path = rospy.get_param("~waypoints_file", DEFAULT_FILE)
        self.dry_run = bool(rospy.get_param("~dry_run", True))
        self.enable_motion = bool(rospy.get_param("~enable_motion", False))
        self.fix_topic = rospy.get_param("~fix_topic", "/fix")
        self.from_ll_service = rospy.get_param("~from_ll_service", "/fromLL")
        self.action_name = rospy.get_param("~action_name", "/move_base")
        self.map_frame = rospy.get_param("~map_frame", "map")
        self.fix_max_age = float(rospy.get_param("~fix_max_age_sec", 5.0))
        self.goal_timeout = float(rospy.get_param("~goal_timeout_sec", 180.0))

        with open(self.file_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        self.example_only = bool(config.get("example_only", True))
        self.waypoints = config.get("waypoints", [])
        if not isinstance(self.waypoints, list) or not self.waypoints:
            raise ValueError("No waypoints in: {}".format(self.file_path))
        for index, wp in enumerate(self.waypoints):
            self._validate_waypoint(wp, index)

        self.last_fix = None
        self.last_fix_receive_time = None
        self.fix_sub = rospy.Subscriber(
            self.fix_topic, NavSatFix, self._fix_callback, queue_size=5)

        self.converter = None
        self.move_base = None

    @staticmethod
    def _validate_waypoint(wp, index):
        if not isinstance(wp, dict):
            raise ValueError("Waypoint {} must be a mapping".format(index))
        for field in ("latitude", "longitude", "map_yaw_deg"):
            if field not in wp:
                raise ValueError("Waypoint {} missing '{}'".format(index, field))
            value = float(wp[field])
            if not math.isfinite(value):
                raise ValueError("Waypoint {} has invalid '{}'".format(index, field))
        lat = float(wp["latitude"])
        lon = float(wp["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Waypoint {} latitude/longitude out of range".format(index))

    def _fix_callback(self, msg):
        self.last_fix = msg
        self.last_fix_receive_time = rospy.Time.now()

    def _valid_recent_fix(self):
        msg = self.last_fix
        if msg is None or self.last_fix_receive_time is None:
            return False
        if msg.status.status < NavSatStatus.STATUS_FIX:
            return False
        if not (math.isfinite(msg.latitude) and math.isfinite(msg.longitude)):
            return False
        return (rospy.Time.now() - self.last_fix_receive_time).to_sec() <= self.fix_max_age

    def _wait_for_fix(self, timeout_sec=30.0):
        start = rospy.Time.now()
        while not rospy.is_shutdown():
            if self._valid_recent_fix():
                return True
            if (rospy.Time.now() - start).to_sec() > timeout_sec:
                return False
            rospy.sleep(0.2)
        return False

    def _build_goal(self, waypoint, point):
        goal = MoveBaseGoal()
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.header.frame_id = self.map_frame
        goal.target_pose.pose.position.x = float(point.x)
        goal.target_pose.pose.position.y = float(point.y)
        goal.target_pose.pose.position.z = 0.0
        # map_yaw_deg is explicitly an angle in the ROS map frame.
        yaw = math.radians(float(waypoint["map_yaw_deg"]))
        q = quaternion_from_euler(0.0, 0.0, yaw)
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]
        return goal

    def _send_and_monitor_goal(self, goal, name):
        self.move_base.send_goal(goal)
        start = rospy.Time.now()
        while not rospy.is_shutdown():
            if self.move_base.wait_for_result(rospy.Duration(0.2)):
                state = self.move_base.get_state()
                if state == GoalStatus.SUCCEEDED:
                    rospy.loginfo("[GNSS] reached %s", name)
                    return True
                rospy.logerr("[GNSS] goal failed: %s (state=%d)", name, state)
                return False
            if not self._valid_recent_fix():
                self.move_base.cancel_goal()
                rospy.logerr("[GNSS] GNSS fix stale or invalid; cancelled goal %s", name)
                return False
            if (rospy.Time.now() - start).to_sec() > self.goal_timeout:
                self.move_base.cancel_goal()
                rospy.logerr("[GNSS] timed out goal %s", name)
                return False
        self.move_base.cancel_goal()
        return False

    def run(self):
        if self.dry_run:
            rospy.logwarn("[GNSS] DRY RUN: listing geodetic waypoints only; NO move_base goals")
            for i, wp in enumerate(self.waypoints, 1):
                rospy.loginfo("[%d] %s lat=%.8f lon=%.8f map_yaw=%.1f deg",
                              i, wp.get("name", "wp{}".format(i)),
                              float(wp["latitude"]), float(wp["longitude"]),
                              float(wp["map_yaw_deg"]))
            return

        # Two independent, explicit interlocks prevent motion with sample coords.
        if not self.enable_motion:
            rospy.logerr("Motion disabled: set ~enable_motion:=true AFTER system checks")
            return
        if self.example_only:
            rospy.logerr("Example coordinates cannot be used for motion. "
                         "Replace them with surveyed waypoints and set example_only: false")
            return
        if not self._wait_for_fix():
            rospy.logerr("No fresh, valid GNSS fix received on %s", self.fix_topic)
            return

        try:
            rospy.wait_for_service(self.from_ll_service, timeout=20.0)
            self.converter = rospy.ServiceProxy(self.from_ll_service, FromLL)
        except (rospy.ROSException, rospy.ServiceException) as exc:
            rospy.logerr("No /fromLL conversion service: %s", exc)
            return

        self.move_base = actionlib.SimpleActionClient(self.action_name, MoveBaseAction)
        if not self.move_base.wait_for_server(rospy.Duration(20.0)):
            rospy.logerr("move_base action unavailable: %s", self.action_name)
            return

        for i, wp in enumerate(self.waypoints, 1):
            if rospy.is_shutdown():
                return
            if not self._valid_recent_fix():
                rospy.logerr("Lost GNSS fix before waypoint %d", i)
                return
            name = str(wp.get("name", "wp{}".format(i)))
            ll = GeoPoint(
                latitude=float(wp["latitude"]),
                longitude=float(wp["longitude"]),
                altitude=float(wp.get("altitude", 0.0)))
            try:
                converted = self.converter(ll)
                point = converted.map_point
                if not (math.isfinite(point.x) and math.isfinite(point.y)):
                    raise ValueError("Non-finite map coordinates")
            except (rospy.ServiceException, ValueError) as exc:
                rospy.logerr("Could not convert waypoint %s to map coordinates: %s", name, exc)
                return

            rospy.loginfo("[GNSS] waypoint %d/%d %s -> map(%.2f, %.2f)",
                          i, len(self.waypoints), name, point.x, point.y)
            if not self._send_and_monitor_goal(self._build_goal(wp, point), name):
                return
        rospy.loginfo("[GNSS] All GNSS waypoints reached")


if __name__ == "__main__":
    rospy.init_node("gnss_waypoint_nav")
    try:
        GNSSWaypointNavigator().run()
    except (ValueError, OSError, yaml.YAMLError) as exc:
        rospy.logfatal("GNSS waypoint configuration error: %s", exc)
