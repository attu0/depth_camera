#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from camera_info_manager import CameraInfoManager


class StereoSplitter(Node):
    def __init__(self):
        super().__init__('stereo_splitter')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, '/image_raw', self.cb, 10)

        self.left_pub = self.create_publisher(Image, '/left/image_raw', 10)
        self.right_pub = self.create_publisher(Image, '/right/image_raw', 10)
        self.left_info_pub = self.create_publisher(CameraInfo, '/left/camera_info', 10)
        self.right_info_pub = self.create_publisher(CameraInfo, '/right/camera_info', 10)

        self.left_info_mgr = CameraInfoManager(self, cname='left', namespace='/left')
        self.left_info_mgr.setURL(
            'file:///home/atharv/Desktop/depth_camera/stereo_ws/src/stereo_camera_pkg/config/calibration/left.yaml'
        )
        self.left_info_mgr.loadCameraInfo()

        self.right_info_mgr = CameraInfoManager(self, cname='right', namespace='/right')
        self.right_info_mgr.setURL(
            'file:///home/atharv/Desktop/depth_camera/stereo_ws/src/stereo_camera_pkg/config/calibration/right.yaml'
        )
        self.right_info_mgr.loadCameraInfo()

    def to_imgmsg(self, img, header, frame_id):
        msg = Image()
        msg.header = header
        msg.header.frame_id = frame_id
        msg.height, msg.width = img.shape[0], img.shape[1]
        msg.encoding = 'bgr8'
        msg.is_bigendian = 0
        msg.step = img.shape[1] * 3
        msg.data = img.tobytes()
        return msg

    def cb(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        h, w = frame.shape[:2]
        mid = w // 2
        left = np.ascontiguousarray(frame[:, :mid])
        right = np.ascontiguousarray(frame[:, mid:])

        left_msg = self.to_imgmsg(left, msg.header, 'left_camera')
        right_msg = self.to_imgmsg(right, msg.header, 'right_camera')

        left_info = self.left_info_mgr.getCameraInfo()
        left_info.header = left_msg.header
        right_info = self.right_info_mgr.getCameraInfo()
        right_info.header = right_msg.header

        self.left_pub.publish(left_msg)
        self.right_pub.publish(right_msg)
        self.left_info_pub.publish(left_info)
        self.right_info_pub.publish(right_info)


def main():
    rclpy.init()
    rclpy.spin(StereoSplitter())


if __name__ == '__main__':
    main()