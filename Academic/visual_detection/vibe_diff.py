import numpy as np
import cv2
import copy
import math
import visual_detection.coordinate_convert as cc

tracking_obj = []   # 正在追踪的前景目标
tracked_obj = []    # 完成追踪的前景目标
obj_num = 0 # 目标总编号
one_frame_block = []    # 每帧处理过的前景目标
overall_roi = None  # 交叉口总体感兴趣区域
lk_mask = np.array([])
corner_mask = np.array([])
M = [] # 坐标转换矩阵

# ShiTomasi角点检测
feature_params = dict( maxCorners = 100, # 最大角点数
                        qualityLevel = 0.3,
                        minDistance = 7,
                        blockSize = 7 )
# lucas_kanade参数
lk_params = dict( winSize = (15,15),
                    maxLevel = 2,   # 金字塔最大层数
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))


class Obj:
    """
    目标类
    """
    def __init__(self, num, type, area, first_frame, first_pos, img, left_up):
        """
        num: 目标编号
        type: 目标类型
        area: 目标面积
        frame_seq: 时间序列
        pos_seq: 位置序列
        last_img: 最后一次成功追踪的图像
        last_left_up: 最后一次成功追踪的左上角坐标
        vel: 速度
        lk_corner: 用于lk光流跟踪的角点
        """
        self.num = num
        self.type = type
        self.area = area
        self.frame_seq = [first_frame]
        self.pos_seq = [first_pos]
        self.last_img = img
        self.last_left_up = left_up
        self.vel = [-1]
        self.use_lk = True
        # 光流角点
        roi_gray = cv2.cvtColor(self.last_img, cv2.COLOR_BGR2GRAY)
        lk_corner = cv2.goodFeaturesToTrack(roi_gray, mask = None, **feature_params)
        try:
            lk_corner += np.array(self.last_left_up)
            lk_corner = np.reshape(lk_corner, (lk_corner.shape[0], 2))
            lk_corner = lk_corner.tolist()
            self.lk_corner = [lk_corner]
        except:
            self.lk_corner = [[]]


    def update(self, frame, pos, area, img, left_up):
        """
        更新目标轨迹
        """
        self.frame_seq.append(frame)
        self.pos_seq.append(pos)
        self.area = area
        self.last_img = img
        self.last_left_up = left_up
        self.vel.append(self.__velocity())

    def update_lk(self, frame_num, lk_corner):
        global lk_mask, corner_mask
        p0 = self.lk_corner[-1]
        p1 = lk_corner
        move = (p1[0][0] - p0[0][0], p1[0][1] - p0[0][1])
        for old, new in zip(p0, p1):
            a, b = old
            c, d = new
            if (a - c) ** 2 + (b - d) ** 2 > 0.05:
                move = (c - a, d - b)
            lk_mask = cv2.line(lk_mask, (int(a), int(b)), (int(c), int(d)), (0, 0, 255), 1)
            corner_mask = cv2.circle(corner_mask,(int(a), int(b)), 2, (255, 255, 0), -1)
        # if frame_num > self.frame_seq[-1] and unmoved / len(p1) < 0.5:
        #     # 未追踪到，依靠lk更新
        #     self.lk_corner.append(lk_corner)   # 更新lk跟踪点
        #     new_center = (self.pos_seq[-1][0] + int(move[0][0]), self.pos_seq[-1][1] + int(move[0][1]))
        #     new_left_up = (self.last_left_up[0] + int(move[0][0]), self.last_left_up[1] + int(move[0][1]))
        #     self.update(frame_num, new_center, self.area, self.last_img, new_left_up)
        if frame_num == self.frame_seq[-1]:
            # 已追踪到，重新计算目标位置
            self.lk_corner.append(lk_corner)    # 更新lk跟踪点
            # if self.area > 200:
            #     self.pos_seq[-1] = (self.pos_seq[-2][0] + move[0], self.pos_seq[-2][1] + move[1])

        # lk_mask = cv2.line(lk_mask, tuple(self.pos_seq[-2]), tuple(self.pos_seq[-1]), (255, 0, 0), 3)
        # end = time.time()
        # print('lk耗时：', round((end - start), 2))

    def __velocity(self):
        """
        前十次跟踪点平均速度
        """
        if len(self.pos_seq) < 10:
            return -1
        distance = 0
        time = 0
        for idx in range(-2, -8, -1):
            # 真实坐标转换
            pre_p = cc.coord_convert(self.pos_seq[idx - 1], M)
            p = cc.coord_convert(self.pos_seq[idx], M)
            next_p = cc.coord_convert(self.pos_seq[idx + 1], M)
            # 均值轨迹平滑
            p1 = ((pre_p[0] + p[0]) / 2, (pre_p[1] + p[1]) / 2)
            p2 = ((p[0] + next_p[0]) / 2, (p[1] + next_p[1]) / 2)
            distance += dist(p1, p2)
            time += (self.frame_seq[idx + 1] - self.frame_seq[idx - 1]) / 2
        new_vel = round(distance / time * 2.9, 1)
        if abs(new_vel - self.vel[-1]) > 3 and self.vel[-1] > 0:
            return self.vel[-1]
        else:
            return new_vel
    def last_lk_corner(self):
        return copy.deepcopy(self.lk_corner[-1])
    def last_vel(self):
        return self.vel[-1]
    def last_pos(self):
        return self.pos_seq[-1]
    def last_frame(self):
        return self.frame_seq[-1]
    def rect_outline(self):
        return self.last_img.shape[-2: : -1]
    def area_diff(self, new_area):
        return abs(new_area - self.area) / min([self.area, new_area])
    def predict_pos(self,frame):
        # frame_diff = frame - self.frame_seq[-1]
        # if len(self.pos_seq) == 1 or self.type == 1:
        #     # 位置不变
        #     return self.pos_seq[-1]
        # elif len(self.pos_seq) == 2:
        #     # 速度不变
        #     return [frame_diff * (2 * self.pos_seq[-1][0] - self.pos_seq[-2][0]), frame_diff * (2 * self.pos_seq[-1][1] - self.pos_seq[-2][1])]
        # else:
        #     # 加速度不变
        #     vel1 = (self.pos_seq[-2][0] - self.pos_seq[-3][0],  self.pos_seq[-2][0] - self.pos_seq[-3][0])
        #     vel2 = (self.pos_seq[-1][0] - self.pos_seq[-2][0],  self.pos_seq[-1][0] - self.pos_seq[-2][0])
        #     accel = (vel2[0] - vel1[0], vel2[1] - vel1[1])
        #     new_pos = self.pos_seq[-1]
        #     for _ in range(int(frame_diff)):
        #         vel2 = (accel[0] + vel2[0], accel[1] + vel2[1])
        #         new_pos = (new_pos[0] + vel2[0], new_pos[1] + vel2[1])
        #     return new_pos
        return self.pos_seq[-1]
    def predict_pos_kalman(self):
        """
        卡尔曼滤波预测位置
        """
        first_pos = self.pos_seq[0]
        if len(self.pos_seq) < 10:  # 大于10个点生效
            return first_pos
        kalman = cv2.KalmanFilter(4,2,0)
        kalman.measurementMatrix = np.array([[first_pos[0],0,0,0],[0,first_pos[1],0,0]],np.float32)
        kalman.transitionMatrix = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]],np.float32)
        kalman.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 0.03
        for pos in self.pos_seq[1:]:
            current_measurement = np.array([[np.float32(pos[0])],[np.float32(pos[1])]])
            kalman.correct(current_measurement)
        return kalman.predict()
    def output_track(self):
        """
        优先输出lk点序列，无连续lk点输出中心点序列
        """
        try:
            x_diff = self.pos_seq[0][0] - self.lk_corner[0][0][0]
            y_diff = self.pos_seq[0][1] - self.lk_corner[0][0][1]
            return [[c[0][0] + x_diff, c[0][1] + y_diff] for c in self.lk_corner]
        except:
            return self.pos_seq

def basic_prepare(filename):
    """
    总体感兴趣区域导入
    坐标变换矩阵导入
    """
    global overall_roi, M
    sub_filename = filename.split('/')[-1][: -4]
    overall_roi = cv2.imread('data/' + sub_filename + '_roi.jpg', cv2.IMREAD_GRAYSCALE)
    M = cc.get_convert_mat(filename, 0)   # 真实坐标转换矩阵

def tracking(filename):
    """
    跟踪主程序
    """
    global one_frame_block, block_num, lk_mask, corner_mask
    basic_prepare(filename)
    cap = cv2.VideoCapture(filename)
    cap_mask = cv2.VideoCapture('E:/1111_4_1_mask.avi')
    # 新建窗口
    cv2.namedWindow('result', 0)
    cv2.namedWindow('mask', 0)
    _, frame = cap.read()
    _, mask_fg = cap_mask.read()
    lk_mask = np.zeros_like(frame)
    # 初始化迭代参数
    old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    while(1):
        _, frame = cap.read()
        _, mask_fg = cap_mask.read()
        frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)    # 读取帧数
        mask_fg = cv2.cvtColor(mask_fg, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转换灰度图
        print('帧: ', frame_num)
        # mask_fg = bg_subtractor.apply(frame, 0.01)        # 提取前景
        mask_fg[mask_fg > 128 ] = 255
        mask_fg[mask_fg < 128 ] = 0
        result = copy.deepcopy(frame)
        corner_mask = np.zeros_like(frame)
        # mask_fg = cv2.GaussianBlur(mask_fg, (3, 3), 0)
        # mask_fg = cv2.medianBlur(mask_fg, 7)    # 中值滤波
        one_frame_block = []
        block_num = 0
        # backgroundImg= bg_subtractor.getBackgroundImage() # 获取背景
        # mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_CLOSE, kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4)))
        # mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_DILATE, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        # 确定前景轮廓
        mask_fg, contours, hierarchy = cv2.findContours(mask_fg,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 前50帧用来训练背景，不做识别跟踪
        if frame_num < 10 :
            cv2.imshow("result", result)
            cv2.imshow('mask', mask_fg)
            if (cv2.waitKey(50) == 27):
                break
            continue
        for cont_s in contours:
            if cont_s.size < 100:
                continue
            # 绘制最小包围矩形
            x,y,w,h = cv2.boundingRect(cont_s)
            roi_img = frame[y: y + h, x: x + w]
            sift_pair(frame_num, cont_s, roi_img, (x, y))
        lk_corners = []
        lk_match_obj = []
        for obj in tracking_obj:
            if frame_num - obj.frame_seq[-1] > 1 or len(obj.frame_seq) == 1 or len(obj.last_lk_corner()) == 0: # 忽略失去跟踪点 or 新建点
                continue
            if len(lk_match_obj) == 0:
                lk_corners = obj.last_lk_corner()
            else:
                lk_corners += obj.last_lk_corner()
            lk_match_obj.append(len(obj.last_lk_corner()))

        if len(lk_corners) != 0:
            a = np.array(lk_corners, dtype = 'float32')
            a = np.reshape(a, (len(lk_corners), 1, 2))
            new_lk_corners, _, _ = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, a, None, **lk_params)
            # for old, new in zip(lk_corners, new_lk_corners):
            #     a, b = new.ravel()
            #     c, d = old.ravel()
                # if (a - c) ** 2 + (b - d) ** 2 < 0.05:
                    # unmoved += 1
                # lk_mask = cv2.line(lk_mask, (a, b), (c, d), (0, 0, 255), 2)
        # except:
            # pass
        match_start = 0
        match_idx = 0
        for obj in tracking_obj:
            if frame_num - obj.frame_seq[-1] <= 1 and len(obj.frame_seq) != 1 and len(obj.last_lk_corner()) != 0:
                new_lk = new_lk_corners[match_start: match_start + lk_match_obj[match_idx]]
                new_lk = np.reshape(new_lk, (lk_match_obj[match_idx], 2))
                new_lk = new_lk.tolist()
                obj.update_lk(frame_num, new_lk)
                match_start += lk_match_obj[match_idx]
                match_idx += 1
            if obj.frame_seq[-1] == frame_num:
                # 目标在当前帧被追踪，显示速度和编号
                rect_color =  (0, 255, 0) if obj.type == 0 else (0, 0, 255)
                r_p = (obj.predict_pos(frame_num + 1))
                c = obj.pos_seq[-1]
                lu = obj.last_left_up
                result = cv2.circle(result, (int(r_p[0]), int(r_p[1])), 5, (0, 255, 0), -1)
                result = cv2.circle(result, (int(c[0]), int(c[1])), 5, (0, 0, 255), -1)
                result = cv2.rectangle(result, (int(lu[0]), int(lu[1])), (int(lu[0]) + obj.rect_outline()[0], int(lu[1]) + obj.rect_outline()[1]), rect_color, 2)
                cv2.putText(result, 'No.' +  str(obj.num), (int(c[0]), int(c[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                # cv2.putText(result, "v:" + str(obj.vel[-1]), (obj.pos_seq[-1][0], obj.pos_seq[-1][1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
                cv2.putText(result, "a:" + str(obj.area), (int(c[0]), int(c[1] - 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        # 图像显示
        # cv2.imshow('back', backgroundImg)
        cv2.putText(result, 'frame:' + str(frame_num), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        old_gray = copy.deepcopy(frame_gray)
        result = cv2.add(result, lk_mask)
        result = cv2.add(result, corner_mask)
        cv2.imshow('result', result)
        cv2.imshow('mask', mask_fg)
        if cv2.waitKey(10) == 27:
            continue
    cv2.destroyAllWindows()
    cap.release()

def frame_cut(filename):
    """
    返回视频第一帧
    """
    cap = cv2.VideoCapture(filename)
    _,  frame = cap.read()
    output = filename.split('/')[-1][: -4]
    cv2.imwrite('data/%s.jpg' % output, frame)

def dist(p1, p2):
    """
    p1, p2距离
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def pair_score(center, area, img, left_up, obj, frame):
    """
    根据距离、面积计算两轮廓匹配程度
    center: 待匹配轮廓中心坐标
    area: 待匹配轮廓面积
    old_contour: 原目标 [num, frame1, x1， y1， area1，img1], [num, frame2, x2， y2， area2, img2]
    weight: 权 （距离， 面积）
    """
    dist = math.sqrt((center[0] - obj.last_pos()[0]) ** 2 + (center[1]- obj.last_pos()[1]) ** 2)   # 距离
    area_diff = abs(area - obj.area) / area  #　面积差
    # matched_sift = sift_match(frame, obj.last_img, obj.last_left_up, img, left_up)
    return (dist * area_diff)

def sift_pair(frame, contour, obj_img, left_up):
    """
    跟踪目标匹配
    frame: 帧数
    contour：待匹配前景区域
    obj_img：前景图像
    left：前景左上角坐标
    return：所有匹配目标的 [编号，中心点，速度, 左上角坐标，矩形框边长]
    """
    global obj_num, block_num, corner_mask
    # 前景中心与面积
    center = np.mean(contour, axis = 0)
    center = center[0].tolist()
    area = cv2.contourArea(contour)
    type = 0 if area > 150 else 1
    dist_threshold = 200
    del_list = []
    update_info = []
    min_idx = 0 # 最匹配轮廓编号
    min_score = 9999  # 最匹配轮廓距当前轮廓距离
    threshold = 999  # 匹配阈值，大于阈值说明无匹配轮廓

    for i in range(len(tracking_obj)):
        obj = tracking_obj[i]
        if i in one_frame_block:    # 旧轮廓只使用一次
            continue
        if frame - obj.last_frame() > 5:  # 超过10帧未更新则认为丢失路径
            del_list.append(i)
            continue
        predict_dist = dist(obj.last_pos(), center)    # 预测位置距离差
        if predict_dist > dist_threshold:
            continue
        new_score = pair_score(center, area, obj_img, left_up, obj, frame)
        if new_score < min_score:
            min_score = new_score
            min_idx = i
    if min_score < threshold:   # 符合阈值则更新轨迹
        update_info.append([min_idx, frame, center, area, obj_img, left_up])
        for info in update_info:
            one_frame_block.append(info[0])
            tracking_obj[info[0]].update(*tuple(info[1: 6]))

    elif overall_roi[center[1]][center[0]] == 255:
        # 添加新轨迹
        # cv2.imshow('img', obj_img)
        # cv2.waitKey(20)
        new_obj = Obj(obj_num, type, area, frame, center, obj_img, left_up)
        tracking_obj.append(new_obj)
        one_frame_block.append(obj_num)
        obj_num += 1    # 总编号+1


    # if len(tracking_obj) != 0:
    #     for idx in range(len(tracking_obj)):
    #         old_obj = tracking_obj[idx]
    #         if old_obj.last_frame() == frame:
    #             # 忽略该帧已处理前景
    #             continue
    #         if frame - old_obj.last_frame() > 5:
    #             # 五帧未更新则停止跟踪
    #             del_list.append(idx)
    #             continue
    #         predict_dist = dist(old_obj.predict_pos(frame) , center)    # 预测位置距离差
    #         if predict_dist < dist_threshold:
    #             # 根据位置关系初步过滤
    #             print('旧模板', old_obj.num)
    #             print('新旧面积', area, old_obj.area)
    #             print('面积比差: ', old_obj.area_diff(area))
    #             print('中心距离差:', predict_dist)
    #             (match_num, x_move, y_move) = sift_match(frame, old_obj.last_img, old_obj.last_left_up, obj_img, left_up)
    #             print('匹配点数: ', match_num)
    #             if predict_dist < min(area, 100) and old_obj.area_diff(area) < 0.3:
    #                 # 基于面积和距离匹配,备选目标依次两两比较
    #                 if len(update_info) == 0:
    #                     update_info.append([idx, frame, center, area, obj_img, left_up, predict_dist])
    #                 elif predict_dist < update_info[0][-1]:
    #                     update_info[0][0] = idx
    #                     update_info[0][-1] = predict_dist
    #             if match_num > 10:
    #                 # 基于sift特征点匹配
    #                 kp_move = [x_move, y_move]
    #                 new_center = (old_obj.last_pos()[0] + kp_move[0], old_obj.last_pos()[1] + kp_move[1])
    #                 new_left_up = (old_obj.last_left_up[0] + kp_move[0], old_obj.last_left_up[1] + kp_move[1])
    #                 update_info.append([idx, frame, new_center, old_obj.area, old_obj.last_img, new_left_up, predict_dist])

    del_list = sorted(del_list, reverse = True)
    for del_obj in del_list:
        tracked_obj.append(tracking_obj[del_obj])
        # print('停止跟踪:', tracking_obj[del_obj].num)
        del tracking_obj[del_obj]
    # print('------------------------')

def is_repeated(tar_obj):
    (x1, y1) = tar_obj.last_left_up
    (w1, h1) = tar_obj.rect_outline()
    flag = False
    for obj in tracking_obj:
        (x2, y2) = obj.last_left_up
        (w2, h2) = obj.rect_outline()
        if tar_obj.num == obj.num or x2 > x1 + w1 or x1 > x2 + w2 or y2 > y1 + h1 or y1 > y2 + h2:
            # 不产生重叠
            continue
        x_l = sorted([x1, x1 + w1, x2, x2 + w2])
        y_l = sorted([y1, y1 + h1, y2, y2 + h2])
        repeat_area = abs((x_l[1] - x_l[2]) * (y_l[1] - y_l[2]))
        repeat_ratio = repeat_area / (w1 * h1)
        if repeat_ratio > 0.6:
            flag = True
            break
    return flag

def sift_match(frame, old_obj_img, old_left_up, new_obj_img, new_left_up):
    """
    frame: 帧号
    xx_img: 目标图像
    xx_left_up: 左上角坐标
    return: 匹配sift点数，sift点位移
    """
    # 计算sift点
    sift = cv2.xfeatures2d.SIFT_create()
    old_kp, old_des = sift.detectAndCompute(old_obj_img, None)
    new_kp, new_des = sift.detectAndCompute(new_obj_img, None)
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    good = []
    try:
        # 新旧图像sift点匹配
        matches = flann.knnMatch(old_des, new_des, k=2)
        matchesMask = [[0,0] for _ in range(len(matches))]
        # ratio test as per Lowe's paper
        for i,(m,n) in enumerate(matches):
            if m.distance < 0.7 * n.distance:
                matchesMask[i]=[1,0]
        draw_params = dict(matchColor = (0,255,0),
            singlePointColor = (255,0,0),
            matchesMask = matchesMask,
            flags = 0)
        # 筛选优质匹配点
        for m,n in matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)
    except:
        pass
    if len(good) == 0:
        # print('无优质匹配点')
        return 0, 0, 0
    # 计算最优点位移
    # good = sorted(good, key = lambda g : g.distance)
    g = good[0]
    kp0 = old_kp[g.queryIdx].pt
    kp1 = new_kp[g.trainIdx].pt
    x_move = kp1[0] + new_left_up[0] - kp0[0] - old_left_up[0]
    y_move = kp1[1] + new_left_up[1] - kp0[1] - old_left_up[1]
    if frame > 680:
        # cv2.imshow('old', old_obj_img)
        # cv2.imshow('new', new_obj_img)
        # 显示匹配效果
        img3 = cv2.drawMatchesKnn(old_obj_img, old_kp, new_obj_img, new_kp, matches,  None, **draw_params)
        cv2.imshow('img3', img3)
        if cv2.waitKey(0) == 27:
            cv2.destroyWindow('img3')
    return len(good), x_move, y_move

def write2file(filename):
    output = filename.split('/')[-1][: -4]
    with open('data/%s_routes.txt' % output, 'w') as f:
        for obj in tracked_obj:
            if len(obj.pos_seq) < 25:
                continue
            f.write(str(obj.num) + ' ' + str(obj.type) + '\n')
            for frame in obj.frame_seq:
                f.write(str(frame) + ' ')
            f.write('\n')
            for pos in obj.output_track():
                f.write(str(int(pos[0])) + ' ' + str(int(pos[1])) + '\t')
            f.write('\n')


# filename = 'D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/test1.avi'
filename = 'D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/1111_4_1.avi'
# frame_cut(filename)
tracking(filename)
write2file(filename)