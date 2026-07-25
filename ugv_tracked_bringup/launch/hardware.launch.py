import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition # <-- Добавлено для условия

def generate_launch_description():
    #pkg_description = FindPackageShare('ugv_tracked_description')
    pkg_bringup = FindPackageShare('ugv_tracked_bringup')
    
    #urdf_path = PathJoinSubstitution([pkg_description, 'urdf', 'ugv_base.urdf.xacro'])
    ekf_config_path = PathJoinSubstitution([pkg_bringup, 'config', 'ekf.yaml'])

    # === АРГУМЕНТЫ ===
    launch_camera_arg = DeclareLaunchArgument(
        'launch_camera', 
        default_value='true',
        description='Launch the camera node'
    )
    launch_camera = LaunchConfiguration('launch_camera')

    # === УЗЛЫ И ИНКЛУДЫ ===

    # URDF и Дерево TF (С флагом sim:=false)
    #rsp_node = Node(
    #    package='robot_state_publisher',
    #    executable='robot_state_publisher',
    #    output='screen',
    #    parameters=[{
    #         'robot_description': Command(['xacro ', urdf_path, ' sim:=false']),
    #         'use_sim_time': False
    #     }]
    # )
    # Публикатор состояния подвижных шарниров (колес)
    #jsp_node = Node(
    #    package='joint_state_publisher',
    #    executable='joint_state_publisher',
    #    name='joint_state_publisher',
    #    parameters=[{'use_sim_time': False}]
    #)

    # Локализация (EKF)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_path, {'use_sim_time': False}],
        remappings=[("odometry/filtered", "/odom")]
    )

    # Лидар SLLidar A1
    sllidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([FindPackageShare('sllidar_ros2'), 'launch', 'sllidar_a1_launch.py'])),
        launch_arguments={'serial_port': '/dev/lidar', 'frame_id': 'laser'}.items()
    )

    # Камера (Твой старый скрипт) - ЗАПУСКАЕТСЯ ТОЛЬКО ЕСЛИ launch_camera:=true
    camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.expanduser('~/ros2_ws/run_camera.launch.py')),
        condition=IfCondition(launch_camera)
    )
    
    # Параметры: X Y Z Yaw Pitch Roll parent_frame child_frame
    # Настрой X, Y, Z (в метрах) рулеткой от центра робота до объектива камеры!
    camera_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_static_tf',
        arguments=['0.15', '0.0', '0.2', '0', '0', '0', 'base_link', 'camera_link'],
        output='screen'
    )

    return LaunchDescription([
        launch_camera_arg,
        #rsp_node,
        #jsp_node,
        ekf_node,
        sllidar_launch,
        camera_launch,
        camera_tf_node
    ])