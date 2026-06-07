import cv2
import numpy as np

cap = cv2.VideoCapture(2)

stereo = cv2.StereoBM_create(numDisparities=16*5, blockSize=15)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    left = frame[:, :w//2]
    right = frame[:, w//2:]

    grayL = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

    disparity = stereo.compute(grayL, grayR)

    disp = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
    disp = np.uint8(disp)

    cv2.imshow("Left", left)
    cv2.imshow("Right", right)
    cv2.imshow("Depth Map", disp)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
