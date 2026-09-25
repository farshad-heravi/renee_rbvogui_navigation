# Copyright (c) 2025, Robotnik Automation S.L.L.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Robotnik Automation S.L.L. nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Robotnik Automation S.L.L. BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch.actions import GroupAction, DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import PythonExpression

from renee_rbvogui_navigation.collision_mode import mode_parameters


def _collision_monitor(context, collision_monitor_config, use_sim):
    # OpaqueFunction so the initial collision_mode goes through the same
    # mode -> *.enabled table as the runtime `collision_mode` switcher.
    mode = LaunchConfiguration('collision_mode').perform(context)
    return [Node(
        package='nav2_collision_monitor',
        executable='collision_monitor',
        name='collision_monitor',
        output='screen',
        parameters=[collision_monitor_config, {'use_sim_time': use_sim},
                    mode_parameters(mode)],
    )]

def generate_launch_description():

    robot_id = LaunchConfiguration("robot_id")
    use_sim = LaunchConfiguration("use_sim")
    config_folder = LaunchConfiguration("config_folder")
    cmd_vel_topic = LaunchConfiguration("cmd_vel_topic")
    use_collision_monitor = LaunchConfiguration("use_collision_monitor")
    collision_monitor_config = LaunchConfiguration("collision_monitor_config")

    # With the collision monitor on, controller_server/behavior_server publish
    # to cmd_vel_nav and collision_monitor forwards (stopped/slowed) commands
    # to the topic named in its config's cmd_vel_out_topic; otherwise they
    # publish straight to cmd_vel_topic as before.
    nav_cmd_vel_topic = PythonExpression([
        "'cmd_vel_nav' if '", use_collision_monitor, "'.lower() == 'true' else '",
        cmd_vel_topic, "'"
    ])

    declared_arguments = [
        # On the real robot, cmd_vel must go to move_base/cmd_vel instead
        # (vogui_ros1_ros2_bridge only relays that topic into the robot's
        # ROS1 twist_mux, so teleop/e-stop still arbitrate over Nav2 — see
        # vogui_ros1_ros2_bridge/config/bridge.yaml).
        DeclareLaunchArgument(
            "cmd_vel_topic",
            default_value="robotnik_base_control/cmd_vel",
            description="cmd_vel topic controller_server/behavior_server publish to"
        ),
        # Pair enable_stamped_cmd_vel: false in the *_real.yaml variants with
        # cmd_vel_topic:=move_base/cmd_vel — the bridge expects plain
        # geometry_msgs/Twist there, not Nav2 Jazzy's default TwistStamped.
        DeclareLaunchArgument(
            "controller_config",
            default_value=PathJoinSubstitution([
                FindPackageShare('renee_rbvogui_navigation'),
                'config/controller_server.yaml'
            ]),
            description="controller_server params file"
        ),
        DeclareLaunchArgument(
            "planner_config",
            default_value=PathJoinSubstitution([
                FindPackageShare('renee_rbvogui_navigation'),
                'config/planner_server.yaml'
            ]),
            description="planner_server params file"
        ),
        DeclareLaunchArgument(
            "bt_nav_to_pose_xml",
            default_value=PathJoinSubstitution([
                FindPackageShare('renee_rbvogui_navigation'),
                'config/behavior_trees/navigate_to_pose.xml'
            ]),
            description="bt_navigator default NavigateToPose behavior tree"
        ),
        DeclareLaunchArgument(
            "behavior_config",
            default_value=PathJoinSubstitution([
                FindPackageShare('renee_rbvogui_navigation'),
                'config/behavior_server.yaml'
            ]),
            description="behavior_server params file"
        ),
        # Real robot only (navigation_real_entrypoint.sh): the rover's own
        # safety lasers/PLC are not active, see collision_monitor_real.yaml.
        DeclareLaunchArgument(
            "use_collision_monitor",
            default_value="false",
            description="Gate Nav2 cmd_vel through nav2_collision_monitor"
        ),
        DeclareLaunchArgument(
            "collision_monitor_config",
            default_value=PathJoinSubstitution([
                FindPackageShare('renee_rbvogui_navigation'),
                'config/collision_monitor_real.yaml'
            ]),
            description="collision_monitor params file"
        ),
        DeclareLaunchArgument(
            "collision_mode",
            default_value="both",
            description="Lasers feeding the collision monitor: both|front|rear|none"
        ),
    ]

    # Nav2 core node configurations

    controller_config = LaunchConfiguration("controller_config")

    planner_config = LaunchConfiguration("planner_config")

    # Nav2 auxiliary node configurations

    behavior_config = LaunchConfiguration("behavior_config")

    smoother_config = PathJoinSubstitution([
        FindPackageShare('renee_rbvogui_navigation'),
        'config/smoother_server.yaml'
    ])

    # Nav2 orchestration node configurations

    bt_navigator_config = PathJoinSubstitution([
        FindPackageShare('renee_rbvogui_navigation'),
        'config/bt_navigator.yaml'
    ])

    bt_navigator_pose_xml = LaunchConfiguration("bt_nav_to_pose_xml")

    bt_navigator_poses_xml = PathJoinSubstitution([
        FindPackageShare('renee_rbvogui_navigation'),
        'config/behavior_trees/navigate_through_poses.xml'
    ])

    # Nav2 core nodes

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[controller_config, {'use_sim_time': use_sim}],
        remappings=[
            ('cmd_vel', nav_cmd_vel_topic),
            ('odom', 'robotnik_base_control/odom'),
        ]
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[planner_config, {'use_sim_time': use_sim}],
    )

    # Nav2 auxiliary nodes

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[behavior_config, {'use_sim_time': use_sim}],
        remappings=[
            ('cmd_vel', nav_cmd_vel_topic)
        ]
    )

    smoother_server = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[smoother_config, {'use_sim_time': use_sim}],
    )


    # Nav2 orchestration nodes

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[
            bt_navigator_config,
            {
                'use_sim_time': use_sim,
                'default_nav_to_pose_bt_xml': bt_navigator_pose_xml,
                'default_nav_through_poses_bt_xml': bt_navigator_poses_xml,
            }
        ],
        remappings=[
            ('odom', 'robotnik_base_control/odom'),
        ]
    )
   
    lifecycle_manager_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[
            {
                'use_sim_time': use_sim,
                'autostart': True,
                'node_names': [
                    'controller_server',
                    'planner_server',
                    'behavior_server',
                    'smoother_server',
                    'bt_navigator'
                ]
            }
        ]
    )

    # Separate lifecycle manager so the sim's node_names list stays untouched.
    collision_monitor = GroupAction(
        condition=IfCondition(use_collision_monitor),
        actions=[
            OpaqueFunction(function=_collision_monitor,
                           args=[collision_monitor_config, use_sim]),
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_collision_monitor',
                output='screen',
                parameters=[{
                    'use_sim_time': use_sim,
                    'autostart': True,
                    'node_names': ['collision_monitor'],
                }]
            ),
        ]
    )

    group = GroupAction([
        controller_server,
        planner_server,
        behavior_server,
        smoother_server,
        bt_navigator,
        lifecycle_manager_navigation,
        collision_monitor
    ])

    return LaunchDescription(declared_arguments + [group])