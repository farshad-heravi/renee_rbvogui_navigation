from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='dual_laser_merger',
            executable='dual_laser_merger_node',
            name='dual_laser_merger_node',
            parameters=[{
                'laser_1_topic': 'front_laser/scan',
                'laser_2_topic': 'rear_laser/scan',
                'merged_scan_topic': 'merged/scan',
                'merged_cloud_topic': 'merged_cloud',
                'target_frame': 'robot_base_footprint',
                'angle_min': -3.141592654,
                'angle_max':  3.141592654,
                'angle_increment': 0.0058,
                'scan_time': 0.05,
                'range_min': 0.1,
                'range_max': 9.0,
                'min_height': -0.5,
                'max_height':  1.5,
                'use_inf': False,
            }],
        )
    ])