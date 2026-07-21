import cv2
import numpy as np

def simple_object_detection(frame):
    """
    简单的物体识别函数
    使用颜色阈值和轮廓检测来识别物体
    """
    # 转换为HSV颜色空间，更容易进行颜色分割
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 定义颜色范围（这里以检测红色物体为例）
    # 红色在HSV中有两个范围
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # 创建掩码
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    # 形态学操作去除噪声
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 在原图上绘制检测到的物体
    for contour in contours:
        # 过滤掉太小的轮廓
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Object', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame

def get_camera_info(cap):
    """
    获取摄像头参数信息
    """
    print("摄像头参数信息:")
    print(f"当前宽度: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"当前高度: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    print(f"当前FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    print(f"亮度: {cap.get(cv2.CAP_PROP_BRIGHTNESS)}")
    print(f"对比度: {cap.get(cv2.CAP_PROP_CONTRAST)}")
    print(f"饱和度: {cap.get(cv2.CAP_PROP_SATURATION)}")
    print(f"色调: {cap.get(cv2.CAP_PROP_HUE)}")
    print(f"增益: {cap.get(cv2.CAP_PROP_GAIN)}")
    print(f"曝光: {cap.get(cv2.CAP_PROP_EXPOSURE)}")



def edge_detection(frame):
    """
    边缘检测函数
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

def main():

    # 打开摄像头设备
    cam_width = 1080
    cam_height = 720

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
    
    get_camera_info(cap)
    print("摄像头预览开始，按以下按键操作：")
    print("1 - 原始预览")
    print("2 - 边缘检测模式")
    print("q - 退出")

    current_mode = 1  # 1:原始, 2:物体识别, 3:边缘检测

    while True:
        # 读取帧
        ret, frame = cap.read()

        if not ret:
            print("无法读取帧")
            break

        # 根据当前模式处理帧
        if current_mode == 1:
            processed_frame = frame
            mode_text = "Original"
        elif current_mode == 2:
            processed_frame = edge_detection(frame)
            mode_text = "Edge Detection"

        # 在画面上显示当前模式
        cv2.putText(processed_frame, f'Mode: {mode_text}', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


        # 设置显示窗口大小为屏幕大小
        cv2.namedWindow('Camera Preview', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Camera Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # 显示处理后的帧
        cv2.imshow('Camera Preview', processed_frame)

        # 键盘输入处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            current_mode = 1
        elif key == ord('2'):
            current_mode = 2

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()