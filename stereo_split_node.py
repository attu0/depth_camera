#!/usr/bin/env python3
"""
stereo_split_node.py

Grabs the combined side-by-side frame from the AR0144 stereo USB camera
(/dev/video2, 2560x720 MJPG) and republishes it as two synced ROS 2 topics:
  /left/image_raw
  /right/image_raw

Usage:
  ros2 run <your_package> stereo_split_node.py
  or just: python3 stereo_split_node.py  (after sourcing your ROS 2 setup)
"""

import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class StereoSplitNode(Node):
    def __init__(self):
        super().__init__('stereo_split_node')

        self.declare_parameter('device', '/dev/video2')
        self.declare_parameter('width', 2560)
        self.declare_parameter('height', 720)
        self.declare_parameter('fps', 30)
        self.declare_parameter('frame_id', 'stereo_camera')

        device = self.get_parameter('device').value
        width = self.get_parameter('width').value
        height = self.get_parameter('height').value
        fps = self.get_parameter('fps').value
        self.frame_id = self.get_parameter('frame_id').value

        self.cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

        if not self.cap.isOpened():
            self.get_logger().error(f'Failed to open {device}')
            raise RuntimeError(f'Could not open {device}')

        actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.get_logger().info(f'Opened {device} at {actual_w}x{actual_h}')
        self.half_w = actual_w // 2

        self.bridge = CvBridge()
        self.left_pub = self.create_publisher(Image, '/left/image_raw', 10)
        self.right_pub = self.create_publisher(Image, '/right/image_raw', 10)

        timer_period = 1.0 / fps
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn('Frame grab failed')
            return

        left_img = frame[:, :self.half_w]
        right_img = frame[:, self.half_w:]

        stamp = self.get_clock().now().to_msg()

        left_msg = self.bridge.cv2_to_imgmsg(left_img, encoding='bgr8')
        left_msg.header.stamp = stamp
        left_msg.header.frame_id = self.frame_id

        right_msg = self.bridge.cv2_to_imgmsg(right_img, encoding='bgr8')
        right_msg.header.stamp = stamp
        right_msg.header.frame_id = self.frame_id

        self.left_pub.publish(left_msg)
        self.right_pub.publish(right_msg)

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = StereoSplitNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
