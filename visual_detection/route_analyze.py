import numpy as np
import cv2
import math
import re
import visual_detection.coordinate_convert as cc

M = []

class Obj:
    def __init__(self, num, type, frame, pos):
        self.num = num
        self.type = type
        self.pos_seq = [[int(pos[p_idx]), int(pos[p_idx + 1])] for p_idx in range(0, len(pos), 2)]
        # self.pos_seq = [cc.coord_convert([int(p[0]), int(p[1])], M) for p in pos if len(p) != 0]
        # print(frame)
        self.frame_seq = [int(float(f)) for f in frame if len(f) != 0]

objs = []

def read_route(filename, span = 25):
    global M, objs
    short_name = filename.replace('_routes', '')
    M = cc.get_convert_mat(short_name, 0)   # 真实坐标转换矩阵
    with open('data/' + filename) as f:
        all_content = f.read().split('\n')
        for i in range(0, len(all_content), 3):
            if len(all_content[i]) == 0:
                break
            num = int(all_content[i].split()[0])
            type = int(all_content[i].split()[1])
            time = all_content[i + 1].split()
            position = all_content[i + 2].split()
            if type == 0 and len(time) < span:
                continue
            new_obj = Obj(num, type, time, position)
            objs.append(new_obj)
    print(len(objs))

def write_clean_data(filename, span = 25):
    read_route(filename, span = span)
    pattern = re.compile('(.+)_routes')
    part_name = re.findall(pattern, filename)[0]
    with open('data/%s_clean_tracked_%d.txt' % (part_name, span), 'w') as f:
        # 坐标数据
        for obj in objs:
            for vec in obj.pos_seq:
                f.write(str(vec[0]) + ' ' + str(vec[1]) + ' ')
            f.write('\n')
    with open('data/%s_direction_data_%d.txt' % (part_name, span), 'w') as f:
        # 位移数据
        for obj in objs:
            pos = obj.pos_seq
            for i in range(len(pos) - 1):
                x_disp = pos[i + 1][0] - pos[i][0]
                y_disp = pos[i + 1][1] - pos[i][1]
                f.write(str(x_disp) + ' ' + str(y_disp) + ' ')
            f.write('\n')
    with open('data/%s_radian_data_%d.txt' % (part_name, span), 'w') as f:
        # 弧度 + 速度数据
        for obj in objs:
            pos = obj.pos_seq
            time = obj.frame_seq
            for i in range(1, len(pos)):
                vel = math.sqrt((pos[i][0] - pos[i - 1][0]) ** 2 + (pos[i][1] - pos[i - 1][1]) ** 2) / (time[i] - time[i - 1])
                radian = math.atan2(pos[i][1] - pos[i - 1][1], pos[i][0] - pos[i - 1][0])
                f.write(str(vel) + ' ' + str(radian) + ' ')
            f.write('\n')

def display_route(filename):
    read_route(filename, 10)
    cap = cv2.VideoCapture('D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/1111_3.avi')
    # 新建背景提取器
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    bg_subtractor.setHistory(500)
    bg_subtractor.setVarThreshold(25)
    bg_subtractor.setDetectShadows(False)
    while(1):
        _,  frame = cap.read()
        mask_fg = bg_subtractor.apply(frame, 0.01)        # 提取前景
        backgroundImg = bg_subtractor.getBackgroundImage()    # 显示背景
        frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)    # 读取帧数
        if frame_num > 10:
            break
    mask = np.zeros_like(backgroundImg)
    for obj in objs:
        pos = obj.pos_seq
        color = (0, 255, 0) if obj.type == 0 else (0, 0, 255)
        for i in range(len(pos) - 1):
            mask = cv2.line(mask, tuple(pos[i]), tuple(pos[i + 1]), color, 2)
    frame = cv2.add(backgroundImg, mask)
    cv2.namedWindow('frame', 0)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)

# write_clean_data('routes_test1.txt', span = 50)
display_route('1111_3_routes.txt')