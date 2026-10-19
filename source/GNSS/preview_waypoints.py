#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline waypoint preview. No ROS, receiver, or robot required.

Local east/north positions are for educational preview only; they are NOT
coordinates in the robot's existing ROS map frame.
"""
import argparse
import math
import os
import yaml

EARTH_RADIUS_M = 6378137.0


def local_xy(lat, lon, origin_lat, origin_lon):
    """Equirectangular tangent-plane approximation over short distances."""
    x = EARTH_RADIUS_M * math.radians(lon - origin_lon) * math.cos(math.radians(origin_lat))
    y = EARTH_RADIUS_M * math.radians(lat - origin_lat)
    return (x, y)


def main():
    parser = argparse.ArgumentParser(description="GNSS waypoint dry-run preview")
    parser.add_argument("waypoints", help="path to waypoints.yaml")
    parser.add_argument("--simulate", action="store_true", help="print interpolated steps; no robot control")
    parser.add_argument("--step-m", type=float, default=2.0, help="preview step length in meters")
    args = parser.parse_args()
    if args.step_m <= 0:
        parser.error("--step-m must be > 0")
    with open(args.waypoints, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    points = data.get("waypoints", [])
    if not points:
        parser.error("No waypoints in YAML")
    origin_lat, origin_lon = float(points[0]["latitude"]), float(points[0]["longitude"])
    print("OFFLINE DEMO only -- coordinates relative to the first waypoint")
    if data.get("example_only", True):
        print("WARNING: Example waypoint coordinates, NOT a surveyed route")
    total = 0.0
    last = None
    for index, wp in enumerate(points, 1):
        x, y = local_xy(float(wp["latitude"]), float(wp["longitude"]), origin_lat, origin_lon)
        distance = math.hypot(x - last[0], y - last[1]) if last else 0.0
        total += distance
        print("{:02d} {:<18s} east={:+8.2f} m north={:+8.2f} m leg={:.2f} m".format(
            index, str(wp.get("name", "wp{}".format(index))), x, y, distance))
        if args.simulate and last is not None:
            steps = max(1, math.ceil(distance / args.step_m))
            for step in range(1, steps + 1):
                t = step / steps
                px = last[0] + t * (x - last[0])
                py = last[1] + t * (y - last[1])
                print("   simulated position {:02d}/{:02d}: east={:+.2f}, north={:+.2f}".format(step, steps, px, py))
        last = (x, y)
    print("Preview route distance: {:.2f} m (straight-line segments)".format(total))
    print("This does NOT test move_base, obstacles, GNSS accuracy, or map alignment.")


if __name__ == "__main__":
    main()
