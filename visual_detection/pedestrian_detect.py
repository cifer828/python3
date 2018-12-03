import cv2
import os
import numpy as np

def is_inside(o, i):
    # 确定某矩形是否包含在另一个矩形中
    ox, oy, ow, oh = o
    ix, iy, iw, ih = i
    return ox > ix and oy > iy and ox + ow < ix + iw and oy + oh < iy + ih

def draw_person(image, person):
    x, y, w, h = person
    cv2.rectangle(image, (x ,y), (x + w, y + h), (0, 255, 255), 2)

def ped_detect(img):
    # 单帧行人检测
    # img = cv2.imread(filename)
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())    # 使用默认行人检测器

    found, w = hog.detectMultiScale(img)
    found_filtered = []
    for ri, r in enumerate(found):
        flag = True
        for qi, q in enumerate(found):
            if is_inside(r, q):
                flag = False
                break
        if flag:
            found_filtered.append(r)
    for person in found_filtered:
        draw_person(img, person)
    cv2.namedWindow('people detection', 0) # 调整窗口大小
    cv2.imshow("people detection", img)
    # cv2.waitKey()

def video_detect(filename):
    # 视频行人检测
    cap = cv2.VideoCapture(filename)
    while(cap.isOpened()):
        ret, frame = cap.read()
        # cv2.imshow('frame', frame)
        ped_detect(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # video_detect('D:\文档\研究生\研二\交通行为参数\数据\交叉口视频\\交叉口4.avi')
    video_detect('D:\文档\研究生\研二\交通行为参数\数据\交叉口视频\\交叉口2.avi')
    # fn = 'C:\\Users\\zhqch\Documents\code\Python3Projects\\visual_detection\input\\image_0.jpg'
    # ped_detect(cv2.imread(fn))