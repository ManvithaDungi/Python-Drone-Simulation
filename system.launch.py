from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='speech_recognition_node', executable='stt'),
        Node(package='command_mapper_node', executable='parser'),
        Node(package='px4_control_node', executable='controller'),
    ])
