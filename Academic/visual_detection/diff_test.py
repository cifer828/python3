import cv2
import copy
import numpy as np
from collections import Counter
import visual_detection.coordinate_convert as cc

tracking_objs = []   # 正在追踪的目标
tracked_objs = []    # 完成追踪的目标
obj_num = 0 # 目标总编号
corners = [] # 每帧KLT角点s
corner2obj = [] # 角点对应的tracking_obj索引
colors = np.random.randint(0,255,(100,3))    #100种随机颜色
lk_params = dict( winSize  = (15, 15), maxLevel = 4, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
feature_params = dict( maxCorners = 500, qualityLevel = 0.2, minDistance = 7, blockSize = 7 )
frame_step = 2

class Obj:
    def __init__(self, num, frame, center, area, rect = 0):
        self.num = num
        self.frame = [frame]
        self.center = [center]
        self.last_area = area
        self.last_rect = rect
        self.lk_corner = []
        self.finished_lk = []

    def add_lk_corner(self, frame, lk_corner):
        self.lk_corner.append([(frame, lk_corner[0], lk_corner[1])])

    def update(self, frame, center, area):
        # 无遮挡时更新
        # if frame == self.frame[-1]:
        #     if center
        # else:
        self.frame.append(frame)
        self.center.append(center)
        self.last_area = area

    def update_shelter(self, frame):
        # 有遮挡时更新
        self.frame.append(frame)
        chosen = 0
        while(len(self.lk_corner[chosen]) < 2 or self.lk_corner[chosen][-1][0] != frame):
            chosen += 1
        cX = self.center[-1][0] - self.lk_corner[chosen][-2][1] + self.lk_corner[chosen][-1][1]
        cY = self.center[-1][1] - self.lk_corner[chosen][-2][2] + self.lk_corner[chosen][-1][2]
        self.center.append((cX, cY))

    def update_lk(self, frame, old_corner, new_corner):
        # 更新角点
        for lc in self.lk_corner:
            if lc[-1][0] == frame - frame_step and lc[-1][1] == old_corner[0] and lc[-1][2] == old_corner[1]:
                lc.append((frame, new_corner[0], new_corner[1]))
                return
        self.lk_corner.append([(frame, new_corner[0], new_corner[1])])

    def finish_lk(self, frame, old_corner):
        idx = 0
        print(old_corner)
        print(self.lk_corner)
        while(True):
            lc = self.lk_corner[idx]
            if lc[-1][0] < frame and lc[-1][1] == old_corner[0] and lc[-1][2] == old_corner[1]:
                self.finished_lk.append(lc)
                break
            idx += 1
        del self.lk_corner[idx]

def basic_prepare(filename, write):
    global overall_roi, M, sub_filename, mask_name, tracking_objs, tracked_objs
    tracked_objs = []
    tracking_objs = []
    sub_filename = filename.split('/')[-1][: -4]
    mask_name = '/'.join(filename.split('/')[: -1]) +  '/' + sub_filename +'_mask' + '.avi'
    overall_roi = cv2.imread('/'.join(filename.split('/')[: -1]) +  '/' + sub_filename +'_roi' + '.jpg', cv2.IMREAD_GRAYSCALE) # 设置感兴趣区域
    # M = cc.get_convert_mat(filename, 0)   # 导入坐标转换矩阵
    if write:
        clear_routes_file(sub_filename) # 清空输出文件

def main(filename, bg_flag = 0, write = False, save_video = False):
    """
    bg_flag: 0 - MOG背景
             1 - Vibe背景
    """
    global corners, obj_num, corner2obj, corner2contour, tracked_objs
    basic_prepare(filename, write)
    cap = cv2.VideoCapture(filename)
    _, frame = cap.read()
    if bg_flag == 1:
        # 读取生成好的vibe背景
        cap_fg = cv2.VideoCapture(mask_name)
        _, mask_fg = cap_fg.read()
    else:
        # MOG背景提取器
        bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        bg_subtractor.setHistory(500)
        bg_subtractor.setVarThreshold(25)
        bg_subtractor.setDetectShadows(False)

    old_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.namedWindow('new_frame', 0)
    cv2.namedWindow('mask', 0)
    # 保存视频
    # fourcc = cv2.CV_FOURCC(*'XVID')
    # 3-宽，4-高，5-帧率
    out_num = 1
    out = cv2.VideoWriter('D:/data/%s/%s_output_%d.avi' % (sub_filename, sub_filename, out_num), 1, cap.get(5), (int(cap.get(3)),int(cap.get(4))))

    while(True):
        _, frame = cap.read()
        if frame is None:
            break
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)
        if bg_flag == 1:
            # vibe
            _, mask_fg = cap_fg.read()
            mask_fg = cv2.cvtColor(mask_fg, cv2.COLOR_BGR2GRAY)
            mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_DILATE, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))
        else:
            # MOG
            mask_fg = bg_subtractor.apply(frame, 0.01)        # 提取前景
            mask_fg = cv2.medianBlur(mask_fg, 9)    # 中值滤波
            mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_DILATE, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        mask_fg[mask_fg > 128 ] = 255
        mask_fg[mask_fg < 128 ] = 0
        mask_fg, contours, hierarchy = cv2.findContours(mask_fg,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        new_corners = []
        new_corner2obj = []
        corner2contour = [] # 角点对应的前景轮廓索引

        train_frame = 20 if bg_flag == 0 else 0
        if frame_num % frame_step == 0 or frame_num < train_frame:
            continue
        if frame_num > 2000 * out_num:  # 分段保存输出
            out_num += 1
            out.release()
            out = cv2.VideoWriter('D:/data/%s/%s_output_%d.avi' % (sub_filename, sub_filename, out_num), 1, cap.get(5), (int(cap.get(3)),int(cap.get(4))))

        # if frame_num > 300:
        #     break

        print('帧:', frame_num, end='\t')

        # 更新旧角点
        if len(corners) > 0:
            p0 = np.float32([cr for cr in corners]).reshape(-1, 1, 2)
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
            p0r, st, err = cv2.calcOpticalFlowPyrLK(frame_gray, old_gray, p1, None, **lk_params)
            d = abs(p0-p0r).reshape(-1, 2).max(-1)
            d2 = abs(p0-p1).reshape(-1, 2).max(-1)
            good = d < 1    # 反算结果是否一致
            good2 = d2 < 0.01   # 角点是否停留不动
            for co, (x0, y0), (x, y), good_flag, good2_flag in zip(corner2obj, p0.reshape(-1, 2), p1.reshape(-1, 2), good, good2):
                if good_flag and co != -1:
                    # 继续跟踪
                    tracking_objs[co].update_lk(frame_num, (x0, y0), (x, y))
                    new_corner2obj.append(co)
                    new_corners.append([x, y])
                    # frame = cv2.line(frame, (int(x0), int(y0)), (int(x), int(y)), (255, 0, 0), 2)
            # 保持corners 和 corner2obj 长度一致
            corners = new_corners
            corner2obj = new_corner2obj

        # 识别新角点
        mask = np.zeros_like(frame_gray)
        mask[:] = 255
        new_p = cv2.goodFeaturesToTrack(frame_gray, mask = mask_fg, **feature_params)
        if new_p is not None:
            new_p = np.float32(new_p).reshape(-1, 2)
            new_p = new_p.tolist()
            # 更新corners
            corners += new_p

        # 为角点分配前景
        for x, y in corners:
            flag = True
            for i in range(len(contours)):
                if cv2.pointPolygonTest(contours[i], (x, y), False) >= 0:
                    corner2contour.append(i)
                    flag = False
                    break
            # -1表示无匹配前景
            if flag:
                corner2contour.append(-1)

        new_corner2obj = [-1 for _ in range(len(corners))]

        for idx in range(len(contours)):
            cont_s = contours[idx]
            area = cv2.contourArea(cont_s)
            if area < 5:   # 忽略小面积轮廓
                continue
            # 轮廓矩计算中心
            M = cv2.moments(cont_s)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # 待显示目标编号与中心点
            draw_No = []
            draw_center = []

            # 与该轮廓匹配的旧角点索引
            pos = [i for i, e in enumerate(corner2contour[:len(corner2obj)]) if e == idx]
            if len(pos) > 0 and overall_roi[cY][cX] > 128:
            # 存在旧角点与轮廓匹配，更新目标
                # 所有匹配目标
                pair_obj = [o[0] for o in Counter([corner2obj[p_idx] for p_idx in pos]).most_common()]
                pair_result = 1
                # 面积法确定最终匹配目标
                temp_area = tracking_objs[pair_obj[0]].last_area
                while(pair_result < len(pair_obj) and area_compare(area, temp_area + tracking_objs[pair_obj[pair_result]].last_area, temp_area)):
                    temp_area += tracking_objs[pair_obj[pair_result]].last_area
                    pair_result += 1
                for p_i in range(pair_result):
                    if pair_result == 1:
                        # 仅匹配单个目标
                        tracking_objs[pair_obj[p_i]].update(frame_num, (cX, cY), area)
                        # 更新角点-目标索引
                        for n_i in range(len(new_corner2obj)):
                            if corner2contour[n_i] == idx:
                                new_corner2obj[n_i] = pair_obj[p_i]
                        # 添加新角点
                        for i, c_idx in enumerate(corner2contour):
                            if c_idx == idx and i >= len(corner2obj):
                                tracking_objs[pair_obj[p_i]].add_lk_corner(frame_num, corners[i])
                    else:
                        # 匹配多个目标（遮挡），不添加新角点（不好确定归属）
                        tracking_objs[pair_obj[p_i]].update_shelter(frame_num)
                        for c_i in range(len(corner2obj)):
                            if corner2obj[c_i] == pair_obj[p_i]:
                                new_corner2obj[c_i] = pair_obj[p_i]
                    draw_No.append(pair_obj[p_i])
                    draw_center.append(tracking_objs[pair_obj[p_i]].center[-1])
            elif len(pos) == 0 and idx in corner2contour and overall_roi[cY][cX] > 128:
            # 前景无匹配，新建目标
                new_obj = Obj(obj_num, frame_num, (cX, cY), area)
                obj_num += 1
                for i, c_idx in enumerate(corner2contour):
                    if c_idx == idx:
                        new_obj.add_lk_corner(frame_num, corners[i])
                tracking_objs.append(new_obj)
                for n_i in range(len(new_corner2obj)):
                    if corner2contour[n_i] == idx:
                        new_corner2obj[n_i] = len(tracking_objs) - 1
                draw_No.append(len(tracking_objs) - 1)
                draw_center.append((cX, cY))
            else:
                continue
                # dict_contour2obj[idx] = obj_choice[0][0] if obj_choice[0][0] != -1 else obj_choice[1][0]
            # 显示轮廓及编号
            color = colors[tracking_objs[draw_No[0]].num % 100].tolist()
            rect = cv2.minAreaRect(cont_s)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame, [box], 0, color, 2)
            for no, d_c in zip(draw_No, draw_center):
                color = colors[tracking_objs[no].num % 100].tolist()
                cv2.putText(frame, 'No.' + str(tracking_objs[no].num),  (int(d_c[0]) + 20, int(d_c[1]) + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                # cv2.putText(frame, '(' +  str(center[0]) + ',' + str(center[1]) + ')', center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                # cv2.putText(frame, 'a:' +  str(tracking_objs[no].last_area), (int(d_c[0]), int(d_c[1]) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        corner2obj = new_corner2obj
        # 显示角点
        for co, (x, y) in zip(corner2obj, corners):
            try:
                color = colors[tracking_objs[co].num % 100].tolist()
            except:
                color = (255, 255, 255)
            # frame = cv2.putText(frame, str(co), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.circle(frame, (int(x), int(y)), 2, color, -1)

        # 删除匹配失败的目标
        del_objs = []
        for idx in range(len(tracking_objs) - 1, -1, -1):
            obj = tracking_objs[idx]
            if obj.frame[-1] < frame_num:
                del_objs.append(idx)
                tracked_objs.append(obj)
                # write_obj(sub_filename, obj)    # 写入文件
                for i in range(len(corner2obj)):    # 调整角点-目标索引
                    corner2obj[i] = corner2obj[i] - 1 if corner2obj[i] > idx else corner2obj[i]
        for del_idx in del_objs:
            # print('删除:' , del_idx)
            del tracking_objs[del_idx]
        # cv2.putText(frame, 'frame:' + str(frame_num), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        if len(tracked_objs) > 0:
            if write:
                # 保存轨迹
                for tobj in tracked_objs:
                    write_obj(sub_filename, tobj)
            tracked_objs = []
        print('tracking:', len(tracking_objs), end = '\t')
        print('tracked:', len(tracked_objs))
        if save_video:
            out.write(frame)
        cv2.imshow('new_frame', frame)
        # cv2.imshow('old_frame', old_frame)
        cv2.imshow('mask', mask_fg)
        old_gray = copy.deepcopy(frame_gray)
        if cv2.waitKey(0) == '27':
            continue
    out.release()

def area_compare(tem_area, area1, area2):
    """
    area1较优为True
    """
    return abs(tem_area - area1) / tem_area < abs(tem_area - area2) / tem_area

def clear_routes_file(output):
     with open('D:/data/%s/%s_routes.txt' % (output, output), 'w') as f:
         f.write('')

def write_obj(output, obj):
    if len(obj.frame) > 5:
        with open('D:/data/%s/%s_routes.txt' % (output, output), 'a') as f:
            f.write('new object' + '\n')
            f.write(str(obj.num) + '\t' + str(obj.last_area) + '\n')
            for frame in obj.frame:
                f.write(str(frame) + '\t')
            f.write('\n')
            for center in obj.center:
                f.write(str(center[0]) + ',' + str(center[1]) + '\t')
            f.write('\n')
            for lk_track in obj.lk_corner:
                for lt in lk_track:
                    f.write(str(lt[0]) + ',' + str(lt[1]) + ',' + str(lt[2]) + '\t')
                f.write('\n')

def mog_compare(filename, f):
    """
    返回mog生成的
    """
    cap = cv2.VideoCapture(filename)
    maskname = filename.replace('.mov','_mask.avi')
    vibe_name = filename.replace('.mov','_vibe.avi')
    my_cap = cv2.VideoCapture(maskname)
    vibe_cap = cv2.VideoCapture(vibe_name)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    bg_subtractor.setHistory(300)
    bg_subtractor.setVarThreshold(25)
    bg_subtractor.setDetectShadows(True)
    bg = np.array([])
    basic_prepare(filename, 0)
    while(1):
        _, frame = cap.read()
        _,my_mask = my_cap.read()
        _,vibe_mask = vibe_cap.read()
        my_mask = cv2.cvtColor(my_mask, cv2.COLOR_BGR2GRAY)
        vibe_mask = cv2.cvtColor(vibe_mask, cv2.COLOR_BGR2GRAY)
        gmm_result = copy.deepcopy(frame)
        vibe_result = copy.deepcopy(frame)
        my_result = copy.deepcopy(frame)
        frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)

        gmm_mask = bg_subtractor.apply(frame, 0.01)        # 提取前景
        # bg = bg_subtractor.getBackgroundImage()
        gmm_mask = cv2.medianBlur(gmm_mask, 9)    # 中值滤波
        gmm_mask = cv2.morphologyEx(gmm_mask, cv2.MORPH_DILATE, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

        gmm_mask[gmm_mask > 128] = 255
        gmm_mask[gmm_mask < 128 ] = 0
        gmm_mask, contours, hierarchy = cv2.findContours(gmm_mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for con in contours:
            M = cv2.moments(con)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            if  overall_roi[cY][cX] > 128:
                rect = cv2.minAreaRect(con)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(gmm_result, [box], 0, [0, 255, 0], 2)

        my_mask[my_mask > 128] = 255
        my_mask[my_mask < 128] = 0
        my_mask, my_contours, hierarchy = cv2.findContours(my_mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for m_con in my_contours:
            M = cv2.moments(m_con)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            if  overall_roi[cY][cX] > 128:
                rect = cv2.minAreaRect(m_con)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(my_result, [box], 0, [0, 255, 0], 2)

        vibe_mask[vibe_mask > 128] = 255
        vibe_mask[vibe_mask < 128] = 0
        vibe_mask, vibe_contours, hierarchy = cv2.findContours(vibe_mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for v_con in vibe_contours:
            M = cv2.moments(v_con)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            if  overall_roi[cY][cX] > 128:
                rect = cv2.minAreaRect(v_con)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(vibe_result, [box], 0, [0, 255, 0], 2)

        gmm_mask = cv2.bitwise_and(gmm_mask, overall_roi)
        my_mask = cv2.bitwise_and(my_mask, overall_roi)
        vibe_mask = cv2.bitwise_and(vibe_mask, overall_roi)
        cv2.putText(bg, str(frame_num), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.namedWindow('gmm', 0)
        cv2.namedWindow('result', 0)
        cv2.namedWindow('my', 0)
        cv2.namedWindow('my_result', 0)
        cv2.namedWindow('vibe', 0)
        cv2.namedWindow('vibe_result', 0)
        cv2.imshow('gmm', gmm_mask)
        cv2.imshow('result', gmm_result)
        cv2.imshow('my', my_mask)
        cv2.imshow('my_result', my_result)
        cv2.imshow('vibe', vibe_mask)
        cv2.imshow('vibe_result', vibe_result)
        if frame_num > f:
            break
        if cv2.waitKey(1) == '27':
            continue
        print(frame_num)
    fn = filename.split('/')[-1][: -4]
    fn_gmm = 'data/' + fn + '/' + str(f) + '_gmm.jpg'
    fn_frame = 'data/' + fn + '/' + str(f) + '_frame.jpg'
    # fn_gmm_mor = 'data/' + fn + '/' + str(f) + '_gmm_mor.jpg'
    fn_gmm_result = 'data/' + fn + '/' + str(f) + '_gmm_result.jpg'
    fn_my = 'data/' + fn + '/' + str(f) + '_my.jpg'
    fn_my_result = 'data/' + fn + '/' + str(f) + '_my_result.jpg'
    fn_vibe = 'data/' + fn + '/' + str(f) + '_vibe.jpg'
    fn_vibe_result = 'data/' + fn + '/' + str(f) + '_vibe_result.jpg'
    cv2.imwrite(fn_frame, frame)
    cv2.imwrite(fn_gmm,gmm_mask)
    cv2.imwrite(fn_gmm_result, gmm_result)
    # cv2.imwrite(fn_my, my_mask)
    # cv2.imwrite(fn_my_result, my_result)
    cv2.imwrite(fn_vibe, vibe_mask)
    cv2.imwrite(fn_vibe_result, vibe_result)

def mog_bg(filename):
    """
    返回mog生成的背景
    """
    cap = cv2.VideoCapture(filename)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    bg_subtractor.setHistory(1000)
    bg_subtractor.setVarThreshold(25)
    bg_subtractor.setDetectShadows(True)
    bg = np.array([])
    basic_prepare(filename, 0)
    for i in range(1000):
        _, frame = cap.read()
        gmm_mask = bg_subtractor.apply(frame, 0.01)        # 提取前景
        bg = bg_subtractor.getBackgroundImage()
        gmm_mask = cv2.medianBlur(gmm_mask, 9)    # 中值滤波
        gmm_mask = cv2.morphologyEx(gmm_mask, cv2.MORPH_DILATE, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        gmm_mask[gmm_mask > 128] = 255
        gmm_mask[gmm_mask < 128 ] = 0
    cv2.imwrite(filename[:-4] + '_bg.jpg', bg)

def one_frame(dir, maskname):
    fn = maskname.split('_')[0]
    frame = cv2.imread(dir + fn + '_frame.jpg')
    mask = cv2.imread(dir + maskname, cv2.IMREAD_GRAYSCALE)
    mask[mask < 128] = 0
    mask[mask > 128] = 255
    mask, contours, hierarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for con in contours:
        rect = cv2.minAreaRect(con)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        frame = cv2.drawContours(frame, [box], 0, [0, 255, 0], 2)
    cv2.imwrite('data/1111_4_2/'+ maskname.replace('.jpg','_result.jpg'), frame)

def frame_cut(filename):
    """
    返回视频第一帧
    """
    cap = cv2.VideoCapture(filename)
    _,  frame = cap.read()
    output = filename.split('/')[-1][: -4]
    cv2.imwrite('D:/data/%s/%s.jpg' % (output, output), frame)

if __name__ == '__main__':
    # read('E:/1111_4_1_mask.avi')
    # main('D:/数据/交叉口视频/1221_2.MOV', bg_flag = 0, write = True)
    # main('D:/data/0440_1/0440_1.mov', bg_flag = 1, write = True)
    # main('D:/data/short/short.MOV', bg_flag = 0, write = False, save_video = True)
    main('D:/data/1111_4_2/1111_4_2.MOV', bg_flag = 1, write = False, save_video = False)
    # mog_bg('D:/data/0329_2/0329_2.MTS')
    # frame_cut('D:/data/0329_2/0329_2.MTS')
    # mog_bg('D:/数据/交叉口视频/1111_4_2.mov', 198)
    # one_frame('data/1111_4_2/', '198_my.jpg')