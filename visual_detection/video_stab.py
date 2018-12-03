import cv2
import numpy as np
from matplotlib import pyplot as plt

lk_params = dict( winSize  = (15, 15), maxLevel = 4, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
feature_params = dict( maxCorners = 1, qualityLevel = 0.5, minDistance = 7, blockSize = 7 )

def main(filename, maskname):
    cap = cv2.VideoCapture(filename)
    mask = cv2.imread(maskname, cv2.IMREAD_GRAYSCALE)
    _, first_img = cap.read()
    first_gray = cv2.cvtColor(first_img, cv2.COLOR_BGR2GRAY)
    mask[mask > 128 ] = 255
    mask[mask< 128 ] = 0
    mask, contours, hierarchy= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    base_points = []
    for con in contours:
        x,y,w,h = cv2.boundingRect(con)
        roi_gray = first_gray[y: y + h, x: x + w]
        p = cv2.goodFeaturesToTrack(roi_gray, mask=None, **feature_params) + np.array([x, y])
        p = p[0][0].tolist()
        base_points.append(p)
        cv2.circle(first_img, (int(p[0]), int(p[1])), 5, [255, 0, 0], -1)
    base_points = np.array(base_points, dtype=np.float32)
    print(base_points)
    while(1):
        _, frame = cap.read()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        p1, _, _ = cv2.calcOpticalFlowPyrLK(first_gray, frame_gray, base_points, None, **lk_params)
        # for new_p in p1:
        #     x, y = new_p.ravel()
        #     cv2.circle(frame, (int(x), int(y)), 3, [255, 0, 0], -1)
        rows, cols, _ = first_img.shape
        # 仿射变换
        M = cv2.getAffineTransform(base_points, p1)
        dst = cv2.warpAffine(frame, M, (cols, rows))
        p2 = cv2.warpAffine(p1, M, (2, 3))
        for new_p in p2:
            x, y = new_p.ravel()
            cv2.circle(dst, (int(x), int(y)), 3, [255, 0, 0], -1)
        # 透视变换
        # M=cv2.getPerspectiveTransform(base_points, p1)
        # dst=cv2.warpPerspective(frame, M, (cols, rows))

        cv2.imshow('result', dst)
        cv2.waitKey(0)
        print('-----------')
        print(p2)



# main('D:/数据/交叉口视频/1214_1_0.avi', 'data/1214_1_0/1214_1_0_mask.jpg')