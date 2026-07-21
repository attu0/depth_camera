import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/atharv/Desktop/depth_camera/stereo_ws/install/stereo_camera_pkg'
