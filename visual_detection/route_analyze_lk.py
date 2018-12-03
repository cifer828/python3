import numpy as np
import cv2
import math

class Corner:
    """
    角点类
    """
    def __init__(self, num, obj_num, start_point, start_frame):
        self.num = num  # 角点编号
        self.obj_num = obj_num  # 所属目标编号
        self.position_seq = [start_point]   # 起始位置
        self.frame_seq = [start_frame]  # 起始时刻
    def add(self, point, frame):
        self.position_seq.append(point)
        self.frame_seq.append(frame)

corner_pos = {}
corner_time = {}
corner_center = {}


def read_route(filename, span = 25):
    with open('data/' + filename) as f:
        all_content = f.read().split('\n')
        for i in range(0, len(all_content), 3):
            if len(all_content[i]) == 0:
                break
            center = all_content[i].split()[2:]
            center = (int(center[0]), int(center[1]))
            obj_num = int(all_content[i].split()[1])
            time = all_content[i + 1].split()
            if len(time) < span:
                continue
            if obj_num in corner_time.keys() and len(corner_time[obj_num]) > len(time):
                continue
            time = [int(float(t)) for t in time if len(t) > 0]
            position = all_content[i + 2].split()
            position = [(int(float(position[idx])), int(float(position[idx + 1]))) for idx in range(0, len(position), 2)]
            corner_pos[obj_num] = position
            corner_time[obj_num] = time
            corner_center[obj_num] = center
    print(len(corner_pos.values()))

def write_clean_data(filename, span = 25):
    read_route(filename, span = span)
    part_name = filename[7: -5]
    with open('data/%s_clean_tracked_%d.txt' % (part_name, span), 'w') as f:
        # 坐标数据
        for pos in corner_pos.values():
            for vec in pos:
                f.write(str(vec[0]) + ' ' + str(vec[1]) + ' ')
            f.write('\n')
    with open('data/%s_direction_data_%d.txt' % (part_name, span), 'w') as f:
        # 位移数据
        for pos in corner_pos.values():
            for i in range(len(pos) - 1):
                x_disp = pos[i + 1][0] - pos[i][0]
                y_disp = pos[i + 1][1] - pos[i][1]
                f.write(str(x_disp) + ' ' + str(y_disp) + ' ')
            f.write('\n')
    with open('data/%s_radian_data_%d.txt' % (part_name, span), 'w') as f:
        # 弧度 + 速度数据
        for num, pos in corner_pos.items():
            time = corner_time[num]
            for i in range(1, len(pos)):
                vel = math.sqrt((pos[i][0] - pos[i - 1][0]) ** 2 + (pos[i][1] - pos[i - 1][1]) ** 2) / (time[i] - time[i - 1])
                radian = math.atan2(pos[i][1] - pos[i - 1][1], pos[i][0] - pos[i - 1][0])
                f.write(str(vel) + ' ' + str(radian) + ' ')
            f.write('\n')

def display_route(filename, span = 25):
    read_route(filename, span)
    cap = cv2.VideoCapture('G:/ZQC/pythonProject/1111_4.mov')
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
        if frame_num > 50:
            break
    color = np.random.randint(0,255,(len(corner_time.keys()),3))
    mask = np.zeros_like(backgroundImg)
    num = 0
    for key, value in corner_pos.items():
        center = corner_center[key]
        x_diff = value[0][0] - center[0]
        y_diff = value[0][1] - center[1]
        for i in range(len(value) - 1):
            p1 = (value[i][0] + x_diff, value[i][1] + y_diff)
            p2 = (value[i + 1][0] + x_diff, value[i + 1][1] + y_diff)
            mask = cv2.line(mask, p1, p2, color[num].tolist(), 2)
        num += 1
    frame = cv2.add(backgroundImg, mask)
    cv2.namedWindow('frame', 0)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)

def hmm_train():
    """
    训练轨迹hmm
    """

# write_clean_data('routes_test1.txt', span = 50)
display_route('lk_routes_1111_4.txt', 200)