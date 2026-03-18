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
        )
    ]

    robot_id = LaunchConfiguration("robot_id")
    use_sim = LaunchConfiguration("use_sim")

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