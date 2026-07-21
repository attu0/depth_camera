from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory('stereo_camera_pkg')
    usb_cam_params = os.path.join(pkg_share, 'config', 'usb_cam_params.yaml')

    usb_cam_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam_node',
        parameters=[usb_cam_params],
        output='screen',
    )

    splitter_node = Node(
        package='stereo_camera_pkg',
        executable='stereo_splitter',
        name='stereo_splitter',
        output='screen',
    )

    stereo_image_proc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('stereo_image_proc'),
                'launch',
                'stereo_image_proc.launch.py',
            )
        ),
        launch_arguments={
            'left_namespace': 'left',
            'right_namespace': 'right',
        }.items(),
    )

    return LaunchDescription([
        usb_cam_node,
        splitter_node,
        stereo_image_proc_launch,
    ])