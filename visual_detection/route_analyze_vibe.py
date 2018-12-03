import numpy as np
import cv2
import math
import re
import visual_detection.coordinate_convert as cc
from visual_detection.diff_test import frame_step

M = []
colors = np.random.randint(0, 255, (100, 3))
part_name = ''
obj_num = 0

class Obj:
    def __init__(self, num, area, frame, pos):
        self.num = int(num)
        self.area = float(area)
        self.pos = [(float(one_pos.split(',')[0]), float(one_pos.split(',')[1])) for one_pos in pos if len(one_pos) > 0]
        # self.pos_seq = [cc.coord_convert([int(p[0]), int(p[1])], M) for p in pos if len(p) != 0]
        # print(frame)
        self.frame = [int(float(f)) for f in frame if len(f) != 0]

    def rewrite(self, frame, pos):
        self.pos = pos
        self.frame = frame

    def edit_pos(self, pos_idx, new_pos):
        self.pos[pos_idx] = new_pos

objs = []

def read_route(filename, span = 25):
    global M, objs, part_name
    pattern = re.compile('(.+)_routes')
    part_name = re.findall(pattern, filename)[0]
    # M = cc.get_convert_mat(part_name + '.mov', 0)   # 真实坐标转换矩阵
    with open('D:/data/' + part_name + '/' + filename) as f:
        all_content = f.read().split('new object')
        for obj_data in all_content:
            if len(obj_data) == 0 :
                continue
            data_list = obj_data.split('\n')
            [num, area] = data_list[1].split('\t')
            frame = data_list[2].split('\t')
            position = data_list[3].split('\t')
            lk_corner = [dl.split('\t')[:-1]for dl in data_list[4: -1]]
            for cor in lk_corner:
                for idx in range(len(cor)):
                    c = cor[idx].split(',')
                    cor[idx] = (float(c[0]), float(c[1]), float(c[2]))
            if len(frame) < span:
                continue
            new_obj = Obj(num, area, frame, position)
            # print(len(new_obj.frame))
            post_process(new_obj, lk_corner)
            # ZX ramp
            # ramp_roi = cv2.imread('D:/data/%s/%s_main.jpg' % (part_name, part_name), cv2.IMREAD_GRAYSCALE)
            # if ramp_roi[int(new_obj.pos[0][1])][int(new_obj.pos[0][0])] > 128:
            # post_process2(new_obj, lk_corner)
            objs.append(new_obj)
    print(len(objs))

def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def post_process2(obj, lk_corner):
    frame =  sorted(list(set(obj.frame)))
    centers = [obj.pos[0]]
    sorted_corners = sorted(lk_corner, key = lambda f:(f[0][0], len(f)))
    current_idx = 0
    current_frame = frame[0]
    while(current_idx < len(sorted_corners) and sorted_corners[current_idx][0][0] == current_frame):
        current_idx += 1
    current_idx -= 1
    centers = adjust_routes(centers, sorted_corners[current_idx])
    while(1):
        if current_idx == len(sorted_corners) - 1:
            break
        current_idx, idx_offset = get_start_idx(sorted_corners, current_idx)
        if idx_offset > len(sorted_corners[current_idx]) - 1:
            break
        centers = adjust_routes(centers, sorted_corners[current_idx][idx_offset: ])
    frame = frame[:len(centers)]
    centers = centers[:len(frame)]
    obj.rewrite(frame, centers)

def get_start_idx(sorted_corners, last_idx):
    last_frame = sorted_corners[last_idx][-1][0]
    new_idx = last_idx + 1
    while(new_idx < len(sorted_corners) and sorted_corners[new_idx][0][0] <= last_frame):
        new_idx += 1
    if new_idx != last_idx + 1:
        new_idx -= 1
    return (new_idx, int((last_frame - sorted_corners[new_idx][0][0]) / frame_step))

def adjust_routes(centers, lk_list):
    diff_x = centers[-1][0] - lk_list[0][1]
    diff_y = centers[-1][1] - lk_list[0][2]
    for (f, x, y) in lk_list[1:]:
        centers.append((x + diff_x, y + diff_y))
    return centers


def post_process(obj, lk_corner):
    """
    路径分离
    """
    idx = 1
    one_route_flag = True
    frame = [obj.frame[0]]
    pos = [obj.pos[0]]
    pos_choice = []
    while(idx < len(obj.frame) - 1):
        pos_choice.append(obj.pos[idx])
        if obj.frame[idx] == obj.frame[idx + 1]:
            one_route_flag == False
            idx += 1
        else:
            closest = min(pos_choice, key=lambda p: dist(p, pos[-1]))
            if dist(closest, pos[-1]) < 30:
                frame.append(obj.frame[idx])
                pos.append(closest)
            pos_choice = []
            idx += 1
    obj.rewrite(frame, pos)
    if one_route_flag and obj.area < 100:
        sorted_corners = sorted(lk_corner, key = lambda f:f[0][0])
        cor_idx = 0
        tolerance = 0
        if obj.num == 334:
            a = 1
        while(True):
            partial_corners = sorted_corners[cor_idx]
            start_idx = int((partial_corners[0][0] - obj.frame[0]) / frame_step)
            end_frame = partial_corners[-1][0]
            if end_frame >= obj.frame[-1] or cor_idx == len(sorted_corners) - 1 or start_idx > len(obj.frame):
                break
            x_diff = obj.pos[start_idx][0] - partial_corners[0][1]
            y_diff = obj.pos[start_idx][1] - partial_corners[0][2]
            o_i = 0
            for i, cor in enumerate(partial_corners):
                if o_i < len(obj.frame) and obj.frame[o_i] == cor[0]:
                    obj.edit_pos(o_i + start_idx, (cor[1] + x_diff, cor[2] + y_diff))
                o_i += 1
            temp_idx = cor_idx
            temp_length = 0
            for r_idx in range(len(sorted_corners) - 1, -1, -1):
                corners = sorted_corners[r_idx]
                if corners[0][0] < sorted_corners[temp_idx][0][0]:
                    break
                elif corners[0][0] <= end_frame + tolerance and len(corners) > temp_length:
                    temp_idx = r_idx
                    temp_length = len(sorted_corners[temp_idx])
            if temp_idx == cor_idx:
                tolerance += frame_step
            else:
                cor_idx = temp_idx
                tolerance = 0
            if tolerance > 10:
                break
    # print(obj.num)

def write_clean_data(filename, span = 25):
    read_route(filename, span = span)
    with open('D:/data/%s/%s_clean_tracked_%d.txt' % (part_name, part_name, span), 'w') as f:
        # 坐标数据
        for obj in objs:
            if len(obj.frame) < span:
                continue
            f.write(str(obj.num) + ' ' + str(obj.area) + '\n')
            for frame in obj.frame:
                f.write(str(frame) + ' ')
            f.write('\n')
            for vec in obj.pos:
                f.write(str(vec[0]) + ' ' + str(vec[1]) + ' ')
            f.write('\n')
    # with open('data/%s/%s_direction_data_%d.txt' % (part_name, part_name, span), 'w') as f:
    #     # 位移数据
    #     for obj in objs:
    #         pos = obj.pos_seq
    #         for i in range(len(pos) - 1):
    #             x_disp = pos[i + 1][0] - pos[i][0]
    #             y_disp = pos[i + 1][1] - pos[i][1]
    #             f.write(str(x_disp) + ' ' + str(y_disp) + ' ')
    #         f.write('\n')
    # with open('data/%s/%s_radian_data_%d.txt' % (part_name, part_name, span), 'w') as f:
    #     # 弧度 + 速度数据
    #     for obj in objs:
    #         pos = obj.pos_seq
    #         time = obj.frame_seq
    #         for i in range(1, len(pos)):
    #             vel = math.sqrt((pos[i][0] - pos[i - 1][0]) ** 2 + (pos[i][1] - pos[i - 1][1]) ** 2) / (time[i] - time[i - 1])
    #             radian = math.atan2(pos[i][1] - pos[i - 1][1], pos[i][0] - pos[i - 1][0])
    #             f.write(str(vel) + ' ' + str(radian) + ' ')
    #         f.write('\n')

def display_route(filename, span = 29):
    read_route(filename, span)
    cap = cv2.VideoCapture('D:/data/' + part_name + '/' + part_name +  '.MTS')
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
        pos = obj.pos
        color = colors[obj.num % 100].tolist()
        for i in range(len(pos) - 1):
            mask = cv2.line(mask, (int(pos[i][0]), int(pos[i][1])), (int(pos[i + 1][0]), int(pos[i + 1][1])), color, 1)
            # mask = cv2.circle(mask, (int(pos[i][0]), int(pos[i][1])), 2, color, 1)
    frame = cv2.add(backgroundImg, mask)
    cv2.namedWindow('frame', 0)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)

# write_clean_data('0328_7_routes.txt', span = 60)
display_route('0328_7_routes.txt', span = 60)