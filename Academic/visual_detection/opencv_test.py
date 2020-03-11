import cv2
import os
import numpy as np

def read_img():
    # 读取图像
    os.chdir('D:\文档\研究生\研二\交通行为参数提取\数据\pedestrians128x64')
    dir_list = os.listdir('.')
    img = cv2.imread(dir_list[0], 0)
    cv2.imshow('image', img)
    cv2.waitKey()
    cv2.destroyAllWindows()

def video_capture():
    # 启用摄像头,保存视频
    cap = cv2.VideoCapture(0)
    # 定义codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('input\output.avi',fourcc, 20.0, (640,480))
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            # frame = cv2.flip(frame, 0) # 旋转图像
            out.write(frame)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    # 释放内存
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def open_video(filename):
    # 读取视频
    cap = cv2.VideoCapture(filename)
    while(cap.isOpened()):
        ret, frame = cap.read()
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # 彩色转黑白
        cv2.namedWindow('frame', 0) # 调整窗口大小
        cv2.imshow('frame', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# open_video('D:\文档\研究生\研二\交通行为参数提取\数据\交叉口视频\\test1.avi')
# video_capture()
print(cv2.__version__)