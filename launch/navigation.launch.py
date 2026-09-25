'''
The code developed by Farshad Nozad Heravi (fnh) for the Renee project.
Email: f.n.heravi@gmail.com
GitHub: https://github.com/farshad-heravi
'''

import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch_ros.actions import PushRosNamespace
from launch.actions import GroupAction

def generate_launch_description():

    declared_arguments = [
        DeclareLaunchArgument(
            "robot_id",
            default_value="",
            description="Name for launch and config resources"
        ),
        DeclareLaunchArgument(
            "use_sim",
            default_value="true",
            description="Enable simulation"
        ),
        # Real-robot overrides (see nav2_task.launch.py for why these exist):
        # navigation_real_entrypoint.sh passes controller/planner/behavior_config
        # pointing at the *_real.yaml variants and cmd_vel_topic:=move_base/cmd_vel.
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
        DeclareLaunchArgument(
            "cmd_vel_topic",
            default_value="robotnik_base_control/cmd_vel",
            description="cmd_vel topic controller_server/behavior_server publish to"
        ),
        # Real-robot collision monitor, see nav2_task.launch.py.
        DeclareLaunchArgument("use_collision_monitor", default_value="false"),
        DeclareLaunchArgument(
            "collision_monitor_config",
            default_value=PathJoinSubstitution([
                FindPackageShare('renee_rbvogui_navigation'),
                'config/collision_monitor_real.yaml'
            ]),
        ),
        DeclareLaunchArgument("collision_mode", default_value="both"),
    ]

    robot_id = LaunchConfiguration("robot_id")
    use_sim = LaunchConfiguration("use_sim")
    controller_config = LaunchConfiguration("controller_config")
    behavior_config = LaunchConfiguration("behavior_config")
    cmd_vel_topic = LaunchConfiguration("cmd_vel_topic")

    # laser_merger = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         PathJoinSubstitution([
    #              FindPackageShare('renee_rbvogui_navigation'), 'launch/laser_merger.launch.py'
    #         ])
    #     )
    # )

    nav2_task = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                 FindPackageShare('renee_rbvogui_navigation'), 'launch/nav2_task.launch.py'
            ])
        ),
        launch_arguments={
            'robot_id': robot_id,
            'use_sim': use_sim,
            'controller_config': controller_config,
            'planner_config': LaunchConfiguration('planner_config'),
            'bt_nav_to_pose_xml': LaunchConfiguration('bt_nav_to_pose_xml'),
            'behavior_config': behavior_config,
            'cmd_vel_topic': cmd_vel_topic,
            'use_collision_monitor': LaunchConfiguration('use_collision_monitor'),
            'collision_monitor_config': LaunchConfiguration('collision_monitor_config'),
            'collision_mode': LaunchConfiguration('collision_mode'),
        }.items()
    )

    nav2_mission = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                 FindPackageShare('renee_rbvogui_navigation'), 'launch/nav2_mission.launch.py'
            ])
        ),
        launch_arguments={
            'robot_id': robot_id,
            'use_sim': use_sim,
        }.items()
    )

    group = GroupAction([
        PushRosNamespace(LaunchConfiguration('robot_id')),
        # laser_merger,
        nav2_task,
        nav2_mission
    ])

    return LaunchDescription(declared_arguments + [group])