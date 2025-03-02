import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    launch_file_dir = os.path.join(get_package_share_directory('osr_gazebo'), 'launch')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    rover_model_path = os.path.join(get_package_share_directory('osr_gazebo'),'models')

    world = os.path.join(
        get_package_share_directory('osr_gazebo'),
        'worlds',
        'empty_world.world'
    )
    set_env_vars_resources = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        rover_model_path)
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r -s -v4 ', world], 'on_exit_shutdown': 'true'}.items()
    )
    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-g -v4 '}.items()
    )

    xacro_file = os.path.join(rover_model_path,
                              'osr_rover',
                              'urdf',
                              'osr.urdf.xacro')

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    params = {'robot_description': doc.toxml()}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )
    spawn_turtlebot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'spawn_rover.launch.py')
        ),
        launch_arguments={
            'x_pose': x_pose,
            'y_pose': y_pose
        }.items()
    )

    # controller_spawn = Node(
    #     package='osr_gazebo',
    #     executable='osr_controller',
    #     output='screen'
    # )

    # joint_state_controller
    # load_joint_state_controller = ExecuteProcess(
    #     cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
    #     output='screen'
    # )
    #
    # # wheel_velocity_controller
    # rover_wheel_controller = ExecuteProcess(
    #     cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'wheel_controller'],
    #     output='screen'
    # )
    #
    # # servo_controller
    # servo_controller = ExecuteProcess(
    #     cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'servo_controller'],
    #     output='screen'
    # )

    return LaunchDescription([
        # controller_spawn,
        # RegisterEventHandler(
        #     event_handler=OnProcessExit(
        #         target_action=spawn_entity,
        #         on_exit=[
        #             load_joint_state_controller,
        #             rover_wheel_controller,
        #             servo_controller,
        #         ],
        #     )
        # ),

        set_env_vars_resources,
        gzserver_cmd,
        gzclient_cmd,
        node_robot_state_publisher,
        spawn_turtlebot_cmd,
    ])
