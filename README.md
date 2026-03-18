# renee_rbvogui_navigation

<!-- Add your recorded simulation navigation video here -->
<!-- Example: ![Navigation Demo](media/navigation_demo.gif) or ![Navigation Demo](media/navigation_demo.mp4) -->

![renee_rbvogui_navigation_lq](https://github.com/user-attachments/assets/139f96fa-719e-4f25-a99d-2fbfcc97554a)


ROS 2 navigation stack for the Renee robot (RB-VOGUI platform). This package provides Nav2-based autonomous navigation, waypoint following, and mission planning for the Robotnik RB-VOGUI mobile base.

---

## Overview

`renee_rbvogui_navigation` integrates the [Nav2](https://navigation.ros.org/) navigation stack with the Renee robot platform. It includes:

- **Path planning** — Global path planning using NavFn (Dijkstra)
- **Local control** — DWB (Dynamic Window Approach) local planner with rotation shim
- **Recovery behaviors** — Spin, backup, drive-on-heading, and wait behaviors
- **Waypoint following** — Sequential navigation through predefined waypoints
- **Route server** — Optional graph-based routing (GeoJSON) for structured environments

The configuration is tuned for the RB-VOGUI footprint and uses `robotnik_base_control` for velocity commands and odometry.

---

## Package Structure

```
renee_rbvogui_navigation/
├── config/                    # Nav2 and behavior configuration
│   ├── behavior_trees/         # Behavior tree XML definitions
│   │   ├── navigate_to_pose.xml
│   │   ├── navigate_through_poses.xml
│   │   └── navigate_routing_planning.xml
│   ├── graph/                 # Route graph (GeoJSON)
│   │   └── demo_map_graph.geojson
│   ├── waypoints/             # Predefined waypoint sequences
│   │   └── demo_map_waypoints.yaml
│   ├── controller_server.yaml
│   ├── planner_server.yaml
│   ├── bt_navigator.yaml
│   ├── behavior_server.yaml
│   ├── smoother_server.yaml
│   ├── waypoint_follower.yaml
│   ├── route_server.yaml
│   ├── rviz_config.rviz
│   └── ...
├── launch/
│   ├── navigation.launch.py   # Main navigation launch (Nav2 task + mission)
│   ├── nav2_task.launch.py    # Nav2 core: planner, controller, BT navigator
│   ├── nav2_mission.launch.py # Waypoint follower, route server
│   └── laser_merger.launch.py # Optional: merge front/rear laser scans
├── world/                     # SDF world files for simulation
│   ├── campetella.sdf
│   └── fnh_world.sdf
└── package.xml
```

---

## Dependencies

- **ROS 2** (tested with Jazzy)
- **Nav2 packages:**
  - `nav2_controller`
  - `nav2_planner`
  - `nav2_behaviors`
  - `nav2_smoother`
  - `nav2_bt_navigator`
  - `nav2_lifecycle_manager`
  - `nav2_waypoint_follower`
  - `nav2_route` (optional)
- **Robot control:** `robotnik_base_control` (for `cmd_vel` and `odom`)
- **Sensors:** Laser scan topic (e.g. `front_laser/scan`)

---

## Launch Arguments

| Argument    | Default | Description                                      |
|------------|---------|--------------------------------------------------|
| `robot_id` | `""`    | Robot namespace (e.g. `robot` for `/robot/...`) |
| `use_sim`  | `true`  | Enable simulation time (`use_sim_time`)         |

---

## Usage

### 1. Launch full navigation stack

```bash
ros2 launch renee_rbvogui_navigation navigation.launch.py
```

With a robot namespace:

```bash
ros2 launch renee_rbvogui_navigation navigation.launch.py robot_id:=robot
```

### 2. Prerequisites

Before launching navigation, ensure:

- **Map server** is running and publishing `/map`
- **TF tree** is correct (`map` → `odom` → `base_link`)
- **Laser scan** is published (e.g. `/robot/front_laser/scan`)
- **Odometry** is published on `robotnik_base_control/odom`

### 3. Sending navigation goals

**Navigate to pose:**

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

**Navigate through poses:**

```bash
ros2 action send_goal /navigate_through_poses nav2_msgs/action/NavigateThroughPoses \
  "{poses: [{header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}]}"
```

**Follow waypoints:**

Use the waypoint follower action with a waypoint sequence (see `config/waypoints/demo_map_waypoints.yaml`).

---

## Configuration Highlights

### Robot footprint

The robot footprint is configured as a rectangle (in meters):

```
[[0.6,-0.35],[0.6,0.35],[-0.6,0.35],[-0.6,-0.35]]
```

### Velocity limits

- **Linear:** max 0.3 m/s
- **Angular:** max 0.2 rad/s

### Controller

- **Primary:** `nav2_rotation_shim_controller::RotationShimController` with `dwb_core::DWBLocalPlanner`
- **Planner:** `nav2_navfn_planner::NavfnPlanner` (Dijkstra)

### Costmaps

- **Local:** 8×8 m rolling window, 0.025 m resolution, obstacle layer from laser
- **Global:** Static layer from `/map`, 0.05 m resolution

### Topic remappings

The launch files remap:

- `cmd_vel` → `robotnik_base_control/cmd_vel`
- `odom` → `robotnik_base_control/odom`

---

## Optional: Laser merger

For robots with front and rear lasers, `laser_merger.launch.py` can merge scans into a single 360° topic. It is currently commented out in `navigation.launch.py` but can be enabled if needed.

---

## Maintainer

**Farshad Nozad Heravi**  
Email: f.n.heravi@gmail.com  
GitHub: [farshad-heravi](https://github.com/farshad-heravi)
