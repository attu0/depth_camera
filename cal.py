#!/usr/bin/env python3

import cv2
import numpy as np
import glob
import os

# ==========================
# CHANGE THIS IF NEEDED
# Number of INNER corners
CHECKERBOARD = (6, 9)
IMAGE_FOLDER = "./images/*.jpg"
OUTPUT_FILE = "camera_calibration.npz"
# ==========================

criteria = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001,
)

objpoints = []
imgpoints = []

objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[
    0:CHECKERBOARD[0],
    0:CHECKERBOARD[1]
].T.reshape(-1, 2)

images = glob.glob(IMAGE_FOLDER)

print(f"Found {len(images)} image(s).")

if len(images) == 0:
    print("No images found!")
    exit()

gray = None

for fname in images:

    img = cv2.imread(fname)

    if img is None:
        print(f"Cannot read {fname}")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(
        gray,
        CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH
        | cv2.CALIB_CB_NORMALIZE_IMAGE,
    )

    if ret:

        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(
            gray,
            corners,
            (11, 11),
            (-1, -1),
            criteria,
        )

        imgpoints.append(corners2)

        cv2.drawChessboardCorners(
            img,
            CHECKERBOARD,
            corners2,
            ret,
        )

        print(f"[OK] {os.path.basename(fname)}")

    else:

        print(f"[FAILED] {os.path.basename(fname)}")

    cv2.imshow("Corners", img)
    cv2.waitKey(300)

cv2.destroyAllWindows()

if len(objpoints) == 0:
    print("\nNo checkerboard detected in any image!")
    exit()

ret, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints,
    imgpoints,
    gray.shape[::-1],
    None,
    None,
)

print("\nCalibration Successful")
print("=" * 50)

print("\nCamera Matrix:\n")
print(cameraMatrix)

print("\nDistortion Coefficients:\n")
print(distCoeffs)

print("\nRMS Error:", ret)

np.savez(
    OUTPUT_FILE,
    camera_matrix=cameraMatrix,
    distortion_coefficients=distCoeffs,
    rvecs=rvecs,
    tvecs=tvecs,
)

print(f"\nCalibration saved to {OUTPUT_FILE}")

# -------------------------
# Reprojection Error
# -------------------------

mean_error = 0

for i in range(len(objpoints)):

    imgpoints2, _ = cv2.projectPoints(
        objpoints[i],
        rvecs[i],
        tvecs[i],
        cameraMatrix,
        distCoeffs,
    )

    error = cv2.norm(
        imgpoints[i],
        imgpoints2,
        cv2.NORM_L2,
    ) / len(imgpoints2)

    mean_error += error

mean_error /= len(objpoints)

print("\nMean Reprojection Error:", mean_error)

