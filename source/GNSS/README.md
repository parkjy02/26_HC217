# GNSS Waypoint Navigation (ROS Noetic)

> **Prototype only — not hardware-tested.** This is new project code (not part of upstream `nmea_navsat_driver`). The existing open-source GNSS driver parses NMEA messages and publishes ROS `sensor_msgs/NavSatFix` messages to `/fix`. This project code reads latitude/longitude waypoints and uses `robot_localization`'s `/fromLL` service and `move_base` to send target goals.

## Files

- `config/waypoints.yaml`: placeholder geodetic waypoints (`example_only: true`)
- `scripts/preview_waypoints.py`: ROS-free waypoint preview and basic interpolated path illustration
- `scripts/gnss_waypoint_nav.py`: ROS navigation node
- `launch/gnss_waypoint_nav.launch`: starts in safe dry-run mode

## A. Check waypoint file in GitHub Codespaces (NO ROS/DEVICE REQUIRED)

From the root of the team repository:

```bash
python3 -m pip install --user PyYAML  # skip if PyYAML is already installed
python3 source/GNSS/gnss_waypoint_navigation/scripts/preview_waypoints.py source/GNSS/gnss_waypoint_navigation/config/waypoints.yaml --simulate
```

This prints local east/north distances **relative to the first sample waypoint**. It does not publish actual ROS goals or move a robot, and **the printed local XY values are not the robot's `map` coordinates**.

## B. ROS Noetic dry run (ROS installed; no GNSS required)

Put this package in an existing `catkin_ws/src` (or symlink it) and build:

```bash
cd ~/catkin_ws/src
ln -s /PATH/TO/26_HC217/source/GNSS/gnss_waypoint_navigation .
cd ~/catkin_ws
catkin_make
source devel/setup.bash
roslaunch gnss_waypoint_navigation gnss_waypoint_nav.launch
```

Default launch arguments are `dry_run:=true`, `enable_motion:=false`. The node only logs the YAML waypoints. A running ROS master is needed, but no GPS, `/fromLL` or `move_base` is required in dry run.

## C. Real-robot integration (NOT YET TESTED)

1. Connect a compatible NMEA GNSS receiver to `nmea_navsat_driver`, configure port and baud rate, and verify that **`/fix`** delivers fresh, valid `sensor_msgs/NavSatFix` messages.
2. Configure localization (`robot_localization` with IMU, wheel odometry, and GNSS) and a **georeferenced** `map` frame. Ensure `navsat_transform_node` exposes a working `/fromLL` (type `robot_localization/FromLL`). Test transformed goal coordinates against known survey points.
3. Run an appropriately configured ROS navigation stack with the `move_base` action server. This project only generates goals; it does not plan obstacle-avoiding paths itself.
4. Replace placeholder waypoints with actual surveyed coordinates and set `example_only: false`. `map_yaw_deg` is a heading relative to the ROS map frame, **not necessarily a compass bearing**.
5. Test in a simulator and under human supervision, with a verified emergency stop. Only after these checks, run:

```bash
roslaunch gnss_waypoint_navigation gnss_waypoint_nav.launch dry_run:=false enable_motion:=true
```

The node cancels goals on timeout, invalid/lost `/fix`, or navigation failure. These basic checks are **not a complete safety system**. GNSS cannot generally be relied upon inside buildings, elevators, or near severe satellite occlusion. The existing indoor AMCL/multi-floor navigation should remain separate or be explicitly integrated through a high-level mode switch.

## Data flow

```text
GNSS receiver -> nmea_navsat_driver -> /fix (NavSatFix)
                                         | 
                      IMU + wheel odometry + EKF / navsat_transform_node
                                         |
waypoints.yaml (lat/lon) -> /fromLL (map x,y) -> move_base -> robot drive
```

**Attribution:** `nmea_navsat_driver` remains separately included under `source/GNSS/nmea_navsat_driver/` with its own upstream license. The scripts in this `gnss_waypoint_navigation` folder are new draft integration code and have not been field validated.
