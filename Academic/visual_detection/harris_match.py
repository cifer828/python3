import cv2
import numpy as np
import copy
import visual_detection.coordinate_convert as cc
import matplotlib.pyplot as plt

tracking_obj = []
tracked_obj = []
one_frame_block = []
num = 0
mask_track = []
# 生成100个随机颜色
colors = np.random.randint(0,255,(10,3))

class Obj:
    sequence = []
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
    def get_last_img(self):
        return self.sequence[-1][-1]
    def get_last_left_up(self):
        return self.sequence[-1][-2]

def vehicle_track():
    global one_frame_block, M, mask_track
    # capture = cv2.VideoCapture("D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/交叉口2.avi")
    capture = cv2.VideoCapture("D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/test1.avi")
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    bg_subtractor.setHistory(500)
    bg_subtractor.setVarThreshold(25)
    bg_subtractor.setDetectShadows(False)
    M = cc.get_convert_mat('', 0)
    _, frame = capture.read()
    mask_track = np.zeros_like(frame)
    while(capture.isOpened()):
        one_frame_block = []
        ret, frame = capture.read()
        frame_num = capture.get(cv2.CAP_PROP_POS_FRAMES)
        if frame_num % 2 == 0:  # 偶数帧效果好？？？
            continue
        mask_fg = bg_subtractor.apply(frame, 0.01)        # 应用MOG2提取前景
        result = copy.deepcopy(frame)
        cv2.namedWindow('result', 0)
        # print('第%s帧' % frame_num)
        # backgroundImg = bg_subtractor.getBackgroundImage()    # 显示背景
        # cv2.imshow("background", backgroundImg)

        mask_fg = cv2.medianBlur(mask_fg, 9)    # 中值滤波
        # 形态学处理
        mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_OPEN, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)))  # 开运算
        # 确定前景轮廓
        mask_fg, contours, hierarchy = cv2.findContours(mask_fg,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_sorted = sorted(contours, key = lambda c : c.size, reverse = True) # 按轮廓面积从大到小排序

        # 前50帧用来训练背景，不做识别跟踪
        # if frame_num < 50 :
        #     cv2.imshow("result", result)
        #     if (cv2.waitKey(50) == 27):
        #         break
        #     continue

        mask_with_rect = np.zeros(frame.shape, np.uint8)    # 新建全黑画布
        for cont_s in contours_sorted:
            # 忽略小面积轮廓
            if cont_s.size < 100 or cont_s.size > 2000:
                break
            # 绘制最小包围矩形
            x,y,w,h = cv2.boundingRect(cont_s)
            mask_with_rect = cv2.rectangle(mask_with_rect, (x, y), (x + w, y + h), (255, 255, 255), -1) # 黑画布绘制检测方块
            result = cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            roi = frame[y: y+h, x: x+w]
            center = [int(x + w /2), int(y + h /2)]
            left_up = [x, y]
            veh_num = feature_pair(frame_num, roi, left_up, center)
            cv2.putText(result, 'No.' +  str(veh_num), tuple(center), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)    # 显示编号
        result = cv2.add(result, mask_track)
        # new_frame = cv2.bitwise_and(frame, mask_with_rect)    # 与运算，仅保留识别方块内图像
        # cv2.namedWindow('new_img', 0)
        # if frame_num != 1.0:
        #     try:
        #         new_img = orb_bf(prev_frame, new_frame)  # orb特征
        #         cv2.imshow('new_img', new_img)
        #     except:
        #         print(frame_num)
        #         pass

        # prev_frame = copy.deepcopy(new_frame)   # 更新前一帧
        # cv2.namedWindow('mask_with_rect', 0)
        # cv2.imshow('mask_with_rect', mask_with_rect)
        # cv2.namedWindow('foreground', 0)
        # cv2.imshow("foreground", mask_fg)
        cv2.imshow("result", result)
        # cv2.namedWindow('video', 0)
        # cv2.imshow("video", frame)
        if (cv2.waitKey(1) == 27):   # Esc退出
            continue

def feature_pair(frame_num, one_car, left_up, center):
    """
    特征匹配追踪
    :param one_car: 单个目标图像
    """
    global num, mask_track
    for obj in tracking_obj:
        (last_x, last_y) = obj.get_last_center()
        if abs(center[0] - last_x) > 100 or abs(center[1] - last_y) > 100:
            continue
        # new_img, match_num = orb_bf(one_car, last_pos[-1])
        try:
            kp, prev_kp, matches = sift_flann(one_car, obj.get_last_img())
            # print('matches: ',match_num)
            # cv2.imwrite('prev_frame.jpg', one_car)
            # cv2.imwrite('frame.jpg', obj.get_last_img())
            # cv2.imshow('new_img', new_img)
            # cv2.waitKey(0)
        except:
            # cv2.imwrite('prev_frame.jpg', one_car)
            # cv2.imwrite('frame.jpg', obj.get_last_img())
            matches = []
        # cv2.imshow('new_img', new_img)
        # cv2.waitKey(0)
        # 匹配成功，追加
        if len(matches) > 10:
            obj.add_one_pos(obj.get_num(), frame_num, center[0], center[1], 0, left_up, one_car)
            # 绘制轨迹
            matches = sorted(matches, key = lambda m : m[0].distance)
            for mat in matches[: 10]:
                img_idx = mat[0].queryIdx
                prev_img_idx = mat[0].trainIdx
                (x1,y1) = kp[img_idx].pt
                (x2,y2) = prev_kp[prev_img_idx].pt
                x1 = int(np.round(x1) + left_up[0])
                y1 = int(np.round(y1) + left_up[1])
                x2 = int(np.round(x2) + obj.get_last_left_up()[0])
                y2 = int(np.round(y2) + obj.get_last_left_up()[1])
                color = colors[obj.get_num() % 10]
                mask_track = cv2.line(mask_track, (x1, y1), (x2, y2), color.tolist(), 2)
                # mask_track = cv2.circle(mask_track, (x1, y1), 2, (255, 0, 0), 2)
                # mask_track = cv2.circle(mask_track, (x2, y2), 2, (0, 0, 255), 2)
            return obj.get_num()
    # 未匹配成功，新建
    num += 1
    new_obj = Obj(num, frame_num, center[0], center[1], 0, left_up, one_car)
    tracking_obj.append(new_obj)
    return num

def sift_flann(prev_frame, frame):
    """
    SIFT特征 + FLANN匹配
    prev_frame：前一帧图像
    frame: 当前帧图像
    """
    # print('Using sift-flann')
    sift = cv2.xfeatures2d.SIFT_create()
    kp, dst = sift.detectAndCompute(frame, None)
    prev_kp, prev_dst = sift.detectAndCompute(prev_frame, None)

    # brute_force匹配
    # bf = cv2.BFMatcher()
    # matches = bf.knnMatch(dst, prev_dst, k = 2)
    # # 比值测试
    # good = []
    # for m, n in matches:
    #     if m.distance < 0.75 * n.distance:
    #         good.append([m])
    # new_img = cv2.drawMatchesKnn(frame, kp, prev_frame, prev_kp, good[: 10], frame,  flags = 2)

    # flann匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 20)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    try:
        matches = flann.knnMatch(dst, prev_dst, k = 2)
    except:
        return [], [], []
    matches_mask = [[0, 0] for _ in range(len(matches))]
    for i, (m, n ) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            matches_mask[i] = [1, 0]
    # draw_params = dict(matchColor = (0, 255, 0), singlePointColor = (255, 0, 0),
    #                    matchesMask = matches_mask, flags = 0)
    # new_img = cv2.drawMatchesKnn(frame, kp, prev_frame, prev_kp, matches, None, **draw_params)
    return kp, prev_kp, matches

def orb_bf(prev_frame, frame):
    """
    orb特征 + brute force匹配
    prev_frame：前一帧图像
    frame: 当前帧图像
    """
    # print('Using orb_bf...')
    orb = cv2.ORB_create()
    kp, dst = orb.detectAndCompute(frame, None)   # 计算特征
    prev_kp, prev_dst = orb.detectAndCompute(prev_frame, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    try:
        matches = bf.match(dst, prev_dst) # 匹配
        matches = sorted(matches, key = lambda x: x.distance)
        new_img = drawMatches(prev_frame, prev_kp, frame, kp, matches)  # 绘图
        return new_img, len(matches)
    except:
        return None, 0

def drawMatches(img1, kp1, img2, kp2, matches):
    # Create a new output image that concatenates the two images together
    # (a.k.a) a montage
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')
    # Place the first image to the left
    out[:rows1,:cols1] = img1
    # Place the next image to the right of it
    out[:rows2,cols1:] = img2

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    for mat in matches:
        # Get the matching keypoints for each of the images
        img1_idx = mat.trainIdx
        img2_idx = mat.queryIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        a = np.random.randint(0,256)
        b = np.random.randint(0,256)
        c = np.random.randint(0,256)

        cv2.circle(out, (int(np.round(x1)),int(np.round(y1))), 2, (a, b, c), 1)      #画圆，cv2.circle()参考官方文档
        cv2.circle(out, (int(np.round(x2)+cols1),int(np.round(y2))), 2, (a, b, c), 1)

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        cv2.line(out, (int(np.round(x1)),int(np.round(y1))), (int(np.round(x2)+cols1),int(np.round(y2))), (a, b, c), 1, shift=0)  #画线，cv2.line()参考官方文档

    # Also return the image if you'd like a copy
    return out

def harris(prev_frame, frame):
    """
    harris角点匹配
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = np.float32(prev_gray)
    prev_dst = cv2.cornerHarris(prev_gray, 2, 3, 0.04)
    dst = cv2.dilate(dst, None)   # 角点加粗显示
    new_frame = copy.deepcopy(frame)
    new_frame[dst > 0.01 * dst.max()] = [0, 0, 255]   # 阈值
    return new_frame

def feature(filename):
    capture = cv2.VideoCapture(filename)
    _, prev_frame = capture.read()
    while(capture.isOpened()):
        ret, frame = capture.read()
        # new_img = sift_flann(frame, prev_frame)
        new_img = orb_bf(frame, prev_frame)
        prev_frame = copy.deepcopy(frame)
        cv2.namedWindow('new_img', 0)
        cv2.imshow('new_img', new_img)
        if cv2.waitKey(100) == 27:
            cv2.destroyAllWindows()
            break

if __name__ == '__main__':
    filename = "D:/文档/研究生/研二/重点研发-交通行为参数/数据/交叉口视频/test1.avi"
    # feature(filename)
    vehicle_track()
    # prev_frame = cv2.imread('prev_frame.jpg')
    # frame = cv2.imread('frame.jpg')
    # # new_img, _ = orb_bf(prev_frame, frame)
    # new_img, _ = sift_flann(prev_frame, frame)
    # cv2.namedWindow('new_img', 0)
    # cv2.imshow('new_img', new_img)
    # cv2.waitKey(0)