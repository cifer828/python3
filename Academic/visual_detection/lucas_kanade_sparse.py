import numpy as np
import cv2
import copy
import math
import re
import visual_detection.coordinate_convert as cc

tracking_corners = [] # 正在追踪的角点
tracked_corners = []  # 完成追踪的角点
tracking_obj = []   # 正在追踪的前景目标
tracked_obj = []    # 完成追踪的前景目标
corner_num = 0 # 角点编号
obj_num = 0 # 前景目标编号
one_frame_block = []    # 每帧处理过的前景目标
M = [] # 坐标转换矩阵
colors = np.random.randint(0,255,(10,3))    #100种随机颜色
vel_dict = {}
mask_track = []
overall_roi = np.array([])

class Obj:
    """
    前景目标类
    """
    def __init__(self, num, frame, x, y, area, left_up, img):
        self.sequence = [[num, frame, x, y, area, left_up, img]]
    def add_one_pos(self, num, frame, x, y, area, left_up, img):
        self.sequence.append([num, frame, x, y, area, left_up, img])
    def get_last_pos(self):
        return self.sequence[-1]
    def get_num(self):
        return self.sequence[0][0]
    def get_last_frame(self):
        return self.sequence[-1][1]
    def get_last_center(self):
        return (self.sequence[-1][2], self.sequence[-1][3])
    def get_last_area(self):
        return self.sequence[-1][4]
    def get_last_sec_center(self):
        return (self.sequence[-2][2], self.sequence[-2][3])

class Corner:
    """
    角点类
    """
    def __init__(self, num, obj_num, start_point, start_frame, obj_center):
        self.num = num  # 角点编号
        self.obj_num = obj_num  # 所属目标编号
        self.position_seq = [start_point]   # 起始位置
        self.frame_seq = [start_frame]  # 起始时刻
        self.obj_center = obj_center    # 目标点中心
    def add(self, point, frame):
        self.position_seq.append(point)
        self.frame_seq.append(frame)
    def last_position(self):
        return self.position_seq[-1]
    def velocity(self):
        """
        :return: 之前十帧的平均速度
        """
        global vel_dict
        if self.length() < 10:
            return -1
        distance = 0
        time = 0
        for idx in range(-2, -8, -1):
            # 真实坐标转换
            pre_p = cc.coord_convert(self.position_seq[idx - 1], M)
            p = cc.coord_convert(self.position_seq[idx], M)
            next_p = cc.coord_convert(self.position_seq[idx + 1], M)
            # 均值轨迹平滑
            (x1, y1) = ((pre_p[0] + p[0]) / 2, (pre_p[1] + p[1]) / 2)
            (x2, y2) = ((p[0] + next_p[0]) / 2, (p[1] + next_p[1]) / 2)
            distance += math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            time += (self.frame_seq[idx + 1] - self.frame_seq[idx - 1]) / 2
        new_vel = round(distance / time * 2.9, 1)
        if self.obj_num not in vel_dict.keys():
            vel_dict[self.obj_num] = new_vel
            return new_vel
        # 速度波动大于3m/s不做记录
        if abs(vel_dict[self.obj_num] - new_vel) < 3:
            vel_dict[self.obj_num] = new_vel
        return vel_dict[self.obj_num]

    def output_position(self):
        for position in self.position_seq:
            yield position
    def output_time(self):
        for frame in self.frame_seq:
            yield frame
    def length(self):
        return len(self.position_seq)


def corner_position():
    """
    返回当前帧中所有角点位置
    """
    positions = []
    for corner in tracking_corners:
        positions.append(corner.last_position())
    positions = np.array(positions)
    return positions.reshape(-1, 1, 2)

def update_corners(p1, old_corners, del_list, frame, idx_list, center_list):
    """
    p1: array, 旧角点的新位置
    old_corners: array, 新检测出的角点
    del_list: list, 待删除的角点序号
    frame: 时刻(帧)
    idx_list: 匹配的前景目标序号
    新角点 = 更新后的原角点 + 新检测出的角点 - 取消跟踪的角点
    :return: 新角点
    """
    global corner_num
    if p1.size == 0:
        new_corners  = old_corners
        new_corners  = new_corners.astype('float32')   # numpy默认float64
    elif old_corners.shape[0] == 0:
        new_corners  = p1
    else:
        p0 = np.vstack((p1, old_corners))
        new_corners = p0.astype('float32')
    # 将取消跟踪的角点转移至已跟踪列表
    for idx in del_list[::-1]:
        tracked_corners.append(tracking_corners[idx])
        del tracking_corners[idx]
    # 更新追踪列表
    new_corners = np.delete(new_corners, del_list, axis = 0)
    obj_idx_start = p1.shape[0] - len(del_list)
    for i in range(new_corners.shape[0]):
        pos =  new_corners[i][0].ravel()
        if i >= len(tracking_corners):
            corner = Corner(corner_num, idx_list[i - obj_idx_start], pos, frame, center_list[i - obj_idx_start])
            tracking_corners.append(corner)
            corner_num += 1    # 更新编号
        else:
            tracking_corners[i].add(pos, frame)
    return new_corners

def basic_prepare(filename):
    """
    总体感兴趣区域导入
    坐标变换矩阵导入
    """
    global overall_roi, M
    sub_filename = filename.split('/')[-1][: -4]
    overall_roi = cv2.imread('/'.join(filename.split('/')[: -1]) +  '/' + sub_filename +'_roi' + '.jpg', cv2.IMREAD_GRAYSCALE) # 设置感兴趣区域
    # M = cc.get_convert_mat(filename, 0)   # 真实坐标转换矩阵

def lucas_kanade(filename):
    """
    稀疏光流跟踪角点
    """
    global one_frame_block, mask_track, M
    cap = cv2.VideoCapture(filename)
    cap_mask = cv2.VideoCapture('D:/data/1111_4_2/1111_4_2_mask.avi')
    # cap = cv2.VideoCapture("D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/交叉口2.avi")
    # cap = cv2.VideoCapture("D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/xcjly.mp4")
    # ShiTomasi角点检测
    feature_params = dict( maxCorners = 100, # 最大角点数
                            qualityLevel = 0.3,
                            minDistance = 5,
                            blockSize = 7 )
    # lucas_kanade参数
    lk_params = dict( winSize = (15,15),
                        maxLevel = 2,   # 金字塔最大层数
                        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    basic_prepare(filename)
    # 读取第一帧，新建前景画布
    _, old_frame = cap.read()
    _, mask_fg = cap_mask.read()
    mask = np.zeros_like(old_frame)
    mask_track = np.zeros_like(old_frame)
    cv2.namedWindow('result', 0)
    # # 新建背景提取器
    # bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    # bg_subtractor.setHistory(500)
    # bg_subtractor.setVarThreshold(25)
    # bg_subtractor.setDetectShadows(True)
    # 初始化迭代参数
    old_gray = np.array([])

    # while(1):
    #     _,  frame = cap.read()
    #     frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)    # 读取帧数
    #     if frame_num < 100:
    #         continue
    #     mask_fg = bg_subtractor.apply(frame, 0.01)        # 提取前景
    #     backgroundImg= bg_subtractor.getBackgroundImage() # 获取背景
    #     cv2.namedWindow('background', 0)
    #     cv2.imshow("background", backgroundImg)
    #     print(frame_num)
    #     if cv2.waitKey(1) == 27:
    #         break

    while(1):
        _,  frame = cap.read()
        _, mask_fg = cap_mask.read()
        frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)    # 读取帧数
        if frame_num > 2000:
            break
        if frame_num < 50:
            continue
        # mask_fg = bg_subtractor.apply(frame, 0.01)        # 提取前景
        result = copy.deepcopy(frame)
        mask_fg = cv2.cvtColor(mask_fg, cv2.COLOR_BGR2GRAY)
        mask_fg[mask_fg != 255] = 0
        # mask_fg = cv2.medianBlur(mask_fg, 9)    # 中值滤波
        # backgroundImg= bg_subtractor.getBackgroundImage() # 获取背景
        # cv2.namedWindow('background', 0)
        # cv2.imshow("background", backgroundImg)
        # 开运算
        # mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_ERODE, kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_DILATE, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        # mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_OPEN, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1)))
        # 确定前景轮廓
        mask_fg, contours, hierarchy = cv2.findContours(mask_fg,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_sorted = sorted(contours, key = lambda c : c.size, reverse = True) # 按轮廓面积从大到小排序
        # 前50帧用来训练背景，不做识别跟踪
        if frame_num < 10 :
            cv2.imshow("result", result)
            if (cv2.waitKey(1) == 27):
                break
            continue
        mask_with_rect = np.zeros(frame.shape, np.uint8)    # 新建全黑画布
        corners = np.array([])
        p1 = np.array([])
        p0r = np.array([])
        one_frame_block = []
        idx_list = []
        center_list = []
        for cont_s in contours_sorted:
            # 忽略小面积轮廓
            if cont_s.size < 5:
                break
            # 绘制最小包围矩形
            x,y,w,h = cv2.boundingRect(cont_s)
            mask_with_rect = cv2.rectangle(mask_with_rect, (x, y), (x + w, y + h), (255, 255, 255), -1)
            roi = frame[y: y + h, x: x + w]
            roi_left_up = [x, y]
            img_center, center, idx = contour_pair(frame_num, cont_s, roi_left_up, roi, 100)
            if idx == -1:
                continue
            # result = cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # cv2.circle(result, tuple(img_center), 10, (0, 255, 0), -1) # 轮廓中心点
            # cv2.putText(result, 'No.' +  str(idx), tuple(img_center), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)    # 显示编号
            # cv2.putText(result, "v:" + str(velocity(idx)), (img_center[0], img_center[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            roi_corners = cv2.goodFeaturesToTrack(roi_gray, mask = None, **feature_params)
            try:
                if roi_corners == None:
                    continue
            except:
                pass
            roi_corners += np.array([x, y])
            idx_list += [idx for _ in range(roi_corners.shape[0])]
            center_list += [img_center for _ in range(roi_corners.shape[0])]
            if corners.size == 0:
                corners = roi_corners
            else:
                corners = np.vstack((corners, roi_corners))
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        p0 = corner_position()
        if p0.size != 0:    # 第三帧开始
            print(frame_num)
            # 更新旧角点位
            p1, _, _ = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
            p0r, _, _ = cv2.calcOpticalFlowPyrLK(frame_gray, old_gray, p1, None, **lk_params)
        del_list = []
        # 绘制轨迹
        for i,(old, new, old2) in enumerate(zip(p0, p1, p0r)):
            a, b = new.ravel()
            c, d = old.ravel()
            e, f = old2.ravel()
            # 更新前后偏移量小则取消跟踪
            if (a - c) ** 2 + (b - d) ** 2 < 0.05 or (c - e) ** 2 + (d - f) ** 2 > 1:
                del_list.append(i)
                continue
            color = colors[tracking_corners[i].obj_num % 10]
            mask = cv2.line(mask, (a, b), (c, d), color.tolist(), 1)
            result = cv2.circle(result,(a, b), 2, color.tolist(), -1)
        update_corners(p1, corners, del_list, frame_num, idx_list, center_list)   # 更新角点
        for oc in corners:
            x, y = oc[0].ravel()
            result = cv2.circle(result, (x, y), 2, [0, 255, 0], -1)  # 新识别出的点
        old_gray = copy.deepcopy(frame_gray)
        # result = cv2.add(result, mask)  # 角点光流轨迹
        # result = cv2.add(result, mask_track)    # 前景中心轨迹
        cv2.namedWindow('mask', 0)
        cv2.imshow('mask', mask_fg)
        cv2.imshow('result', result)
        # print('del:', len(del_list))
        if cv2.waitKey(0) == 27:
            continue
    cv2.destroyAllWindows()
    cap.release()

def velocity(obj_num):
    """
    :return: 目标速度
    """
    obj_corners = [corners for corners in tracking_corners if corners.obj_num == obj_num]
    if len(obj_corners) == 0:
        return -1
    obj_corners = sorted(obj_corners, key = lambda c : c.length(), reverse = True)
    longest_corner = obj_corners[0]
    return longest_corner.velocity()

def pair_score(center, area, obj, weight = (1, 1)):
    """
    根据距离、面积计算两轮廓匹配程度
    center: 待匹配轮廓中心坐标
    area: 待匹配轮廓面积
    old_contour: 原目标 [num, frame1, x1， y1， area1，img1], [num, frame2, x2， y2， area2, img2]
    weight: 权 （距离， 面积）
    """
    dist = math.sqrt((center[0] - obj.get_last_center()[0]) ** 2 + (center[1]- obj.get_last_center()[1]) ** 2)   # 距离
    area_diff = abs(area - obj.get_last_area())   #　面积差
    return dist * weight[0] + area_diff * weight[1]

def contour_pair(frame_num, new_contour, roi_left_up, roi, search_range):
    """
    frame_num: 帧数
    new_contours: 待匹配的前景轮廓
    search_range: 方形搜索窗口边长
    :return: 图像中心， 真实中心, 编号
    """
    global obj_num, mask_track
    area = cv2.contourArea(new_contour)
    img_center = new_contour.sum(axis=0) / new_contour.shape[0]
    img_center = [int(img_center[0][0]), int(img_center[0][1])]
    center = img_center # 无转换
    min_idx = 0 # 最匹配轮廓编号
    min_score = 9999  # 最匹配轮廓距当前轮廓距离
    threshold = 999  # 匹配阈值，大于阈值说明无匹配轮廓
    del_list = [] # 当前帧丢失的路径
    for i in range(len(tracking_obj)):
        obj = tracking_obj[i]
        if i in one_frame_block:    # 旧轮廓只使用一次
            continue
        if frame_num - obj.get_last_frame() > 5:  # 超过5帧未更新则认为丢失路径
            del_list.append(i)
            continue
        if abs(center[0] - obj.get_last_center()[0]) > search_range or abs(center[1] - obj.get_last_center()[1]) > search_range:
            # 旧路径最后一点的中心不得超出新轮廓的搜索窗口
            # print('out of window')
            continue
        new_score = pair_score(center, area, obj)
        if new_score < min_score:
            min_score = new_score
            min_idx = i
    num = obj_num
    if min_score < threshold:   # 符合阈值则更新轨迹
        num = tracking_obj[min_idx].get_num()
        tracking_obj[min_idx].add_one_pos(num, frame_num, center[0], center[1], area, roi_left_up, roi)
        # 绘制两帧间轨迹
        color = colors[num % 10]
        mask_track = cv2.line(mask_track, tracking_obj[min_idx].get_last_sec_center(), tracking_obj[min_idx].get_last_center(), color.tolist(), 2)
    elif overall_roi[center[1]][center[0]] < 128:
        return (0, 0), (0, 0), -1
    else:
        # 添加新轨迹
        min_idx = len(tracking_obj)
        new_obj = Obj(obj_num, frame_num, center[0], center[1], area, roi_left_up, roi)
        tracking_obj.append(new_obj)
        obj_num += 1    # 总编号+1
    # 向tracked_obj添加，并从tracking_obj列表中删除丢失路径
    for del_track in del_list[::-1]:
        tracked_obj.append(tracking_obj[del_track])
        del tracking_obj[del_track]
    # print([num, frame_num, center[0], center[1], area])
    one_frame_block.append(min_idx)
    # print(one_frame_block)
    return img_center, center, num

def write2file(filename):
    output = filename.split('/')[-1][: -4]
    with open('data/lk_routes_%s.txt' % output, 'w') as f:
        for corner in tracked_corners:
            if corner.length() < 29:
                continue
            f.write(str(corner.num) + ' ' + str(corner.obj_num) + ' ' + str(corner.obj_center[0]) + ' ' + str(corner.obj_center[1]) + '\n')
            for frame in corner.output_time():
                f.write(str(frame) + ' ')
            f.write('\n')
            for pos in corner.output_position():
                f.write(str(pos[0]) + ' ' + str(pos[1]) + '\t')
            f.write('\n')

# filename = 'D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/test1.avi'
filename = 'D:/data/1111_4_2/1111_4_2.MOV'
lucas_kanade(filename)
write2file(filename)
