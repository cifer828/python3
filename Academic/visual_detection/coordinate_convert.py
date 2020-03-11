import cv2
import numpy as np

"""
坐标转换
"""

img_coord_file = ''   # 坐标文件名
convert_click = 0   # 坐标转换时点击标定点次数

def mouseclick(event, x, y, s, p):
    """
    左上角点顺时针点击四个标定点，获取点的图像坐标
    """
    global convert_click
    if event == cv2.EVENT_LBUTTONDOWN:
        # if convert_click == 4:
        #     return
        with open(img_coord_file, 'a') as f:
            f.write(str(x) + '\t' + str(y) + '\n')
        convert_click += 1

def get_image_points(path, txt_name):
    """
    获取四个标定点图像坐标写入txt
    需左上角开始顺时针点击
    one_frame: 一帧图像
    """
    global convert_click, img_coord_file
    folder_name = path.split('/')[-1]
    video_filename = path + '/' + folder_name + '.jpg'
    one_frame = cv2.imread(video_filename)
    img_coord_file = path + '/' + txt_name
    convert_click = 0
    with open(img_coord_file, 'w') as f:
        f.write('')
    cv2.namedWindow('input', 0)
    cv2.setMouseCallback("input", mouseclick)
    cv2.imshow('input', one_frame)
    cv2.waitKey(0)

if __name__ == "__main__":
    # convert_test()
    get_image_points('data/jiaoda', 'img.txt') # 点四个点标定
