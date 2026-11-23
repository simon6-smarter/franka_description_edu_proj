#  Copyright (c) 2023 Franka Robotics GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""双臂 FR3 的可视化入口。

只新增本文件，原有 visualize_franka.launch.py 保持不变（单臂仍可照常用）。
用法：ros2 launch franka_description visualize_franka_dual_arm.launch.py
"""

import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchContext, LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration


def robot_state_publisher_spawner(context: LaunchContext):
    robot_type = LaunchConfiguration('robot_type').perform(context)
    load_gripper = LaunchConfiguration('load_gripper').perform(context)
    ee_id = LaunchConfiguration('ee_id').perform(context)

    franka_xacro_filepath = os.path.join(
        get_package_share_directory('franka_description'),
        'robots',
        robot_type,
        robot_type + '.urdf.xacro',
    )
    robot_description = xacro.process_file(
        franka_xacro_filepath,
        mappings={'hand': load_gripper, 'ee_id': ee_id},
    ).toprettyxml(indent='  ')

    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
        )
    ]


def generate_launch_description():
    rviz_file = os.path.join(
        get_package_share_directory('franka_description'),
        'rviz',
        'visualize_franka_dual.rviz',
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'robot_type',
                default_value='fr3_dual_arm',
                description='Robot model to visualize. Default: fr3_dual_arm',
            ),
            DeclareLaunchArgument(
                'load_gripper',
                default_value='true',
                description='Whether to attach the Franka hand end-effector',
            ),
            DeclareLaunchArgument(
                'ee_id',
                default_value='franka_hand',
                description='End-effector id: none / franka_hand / cobot_pump',
            ),
            OpaqueFunction(function=robot_state_publisher_spawner),
            Node(
                package='joint_state_publisher_gui',
                executable='joint_state_publisher_gui',
                name='joint_state_publisher_gui',
            ),
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['--display-config', rviz_file],
            ),
        ]
    )
