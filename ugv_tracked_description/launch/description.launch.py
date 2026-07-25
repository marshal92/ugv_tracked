import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    # Searching for our new package
    pkg_share = get_package_share_directory('ugv_tracked_description')
    
    # Path to the main robot file we created
    xacro_file = os.path.join(pkg_share, 'urdf', 'ugv_base.urdf.xacro')
    
    # Command for compiling xacro "on the fly"
    robot_description = {'robot_description': Command(['xacro ', xacro_file])}
    
    # State Publisher (publishes TF tree)
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )
    
    # Joint State Publisher GUI 
    jsp_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )
    
    return LaunchDescription([
        rsp_node,
        jsp_gui_node,
        rviz_node
    ])