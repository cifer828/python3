#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/12 11:38
# @Author  : Cifer
# @File    : gmm_tracking.py
# @Object  : Using background subtraction and optimal flow to track moving objects in a video.
#            Supoort both fully-auto detection and semi-auto detection (user can pause video can select untracked objects)
# @Output  : Data file include trajectories, speed, acceleration, area of moving objects
#            Video file shows the process of tracking
# See sample video on https://www.youtube.com/watch?v=xF4hOx3RGHw
# See more detail in https://journals.sagepub.com/doi/abs/10.1177/0361198119838979

import copy

import cv2
import dlib
import numpy as np
import pandas as pd

frame_step = 3  # using large stem are fast but inaccurate
tracker_list = []  # list of trackers
tracking_objs = []  # list of tracked objects


def run(im, multi=False):
    """
    :param im:  input image
    :param multi: multiple objects in video or not
    Pause the running video to manually select moving object
    """

    im_disp = im.copy()
    im_draw = im.copy()
    window_name = "Select Tracking Objects"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, im_draw)
    # List containing top-left and bottom-right to crop the image.
    pts_1 = []
    pts_2 = []
    rects = []
    run.mouse_down = False

    def callback(event, x, y, flags, param):
        """
        Callback function of pausing video
        """

        if event == cv2.EVENT_LBUTTONDOWN:
            if not multi and len(pts_2) == 1:
                # one object
                print("Cannot process mutiple objects in one object mode\n Press 'd' to delete selected object")
                return
            run.mouse_down = True
            pts_1.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP and run.mouse_down:
            # add a boundary point of selecting box
            run.mouse_down = False
            pts_2.append((x, y))
            print("Object is at [{}, {}]".format(pts_1[-1], pts_2[-1]))
        elif event == cv2.EVENT_MOUSEMOVE and run.mouse_down:
            # display the paused frame
            im_draw = im.copy()
            cv2.rectangle(im_draw, pts_1[-1], (x, y), (0, 255, 0), 1)
            cv2.imshow(window_name, im_draw)

    cv2.setMouseCallback(window_name, callback)

    while True:
        # display selected box in video
        # window_name_2 = "Selected Objects."
        for pt1, pt2 in zip(pts_1, pts_2):
            rects.append([pt1[0], pt2[0], pt1[1], pt2[1]])
            cv2.rectangle(im_disp, pt1, pt2, (255, 255, 255), 3)

        key = cv2.waitKey(30)
        if key == ord('p'):
            # Press key `s` to return the selected points
            cv2.destroyAllWindows()
            point = [(tl + br) for tl, br in zip(pts_1, pts_2)]
            corrected_point = check_point(point)
            return corrected_point
        elif key == ord('q'):
            # press key 'q ' to quit editing mode
            print("Quit")
            exit()
        elif key == ord('d'):
            # press 'd' to delete selected objects
            if run.mouse_down == False and pts_1:
                print("Object is at [{}, {}]".format(pts_1[-1], pts_2[-1]))
                pts_1.pop()
                pts_2.pop()
                im_disp = im.copy()
            else:
                print("No objects to be deleted")
    cv2.destroyAllWindows()
    point = [(tl + br) for tl, br in zip(pts_1, pts_2)]
    corrected_point = check_point(point)
    return corrected_point


def check_point(points):
    """
    :param points: image points to be tracked
    :return: points list in order
    """
    out = []
    for point in points:
        # find the max and min x
        if point[0] < point[2]:
            minx = point[0]
            maxx = point[2]
        else:
            minx = point[2]
            maxx = point[0]
        # find the max and min y
        if point[1] < point[3]:
            miny = point[1]
            maxy = point[3]
        else:
            miny = point[3]
            maxy = point[1]
        out.append((minx, miny, maxx, maxy))
    return out


class Rect:
    """
    Helper class to wrap a rectangle
    """

    def __init__(self, left, right, top, bottom, margin=0):
        self.__left = int(left) - margin
        self.__right = int(right) + margin
        self.__top = int(top) - margin
        self.__bottom = int(bottom) + margin

    def left(self):
        return self.__left

    def right(self):
        return self.__right

    def top(self):
        return self.__top

    def bottom(self):
        return self.__bottom

    def update(self, left, right, top, bottom):
        self.__init__(left, right, top, bottom)

    def to_list(self):
        return [self.__left, self.__right, self.__top, self.__bottom]


class Obj:
    """
    Core class for tracking moving objects
    """
    num = 0

    def __init__(self, type, frame_num, rect):
        self.id = type + str(Obj.num)
        Obj.num += 1
        self.frame_num = [frame_num]
        self.center = [self.rect_center(rect)]
        self.area = self.rect_area(rect)
        self.rect = rect
        self.rect_list = rect.to_list()

    def update(self, frame_num, rect_list):
        self.frame_num.append(frame_num)
        self.rect.update(*rect_list)
        self.center.append(self.rect_center(self.rect))

    def write(self, output_file):
        # write result file after tracking finished
        if len(self.frame_num) > 30:
            with open(output_file, 'a') as f:
                f.write(str(self.id) + " " + ' '.join([str(p) for p in self.rect_list]) + '\n')
                for frame in self.frame_num:
                    f.write(str(frame) + ' ')
                f.write('\n')
                for center in self.center:
                    f.write(str(center[0]) + ' ' + str(center[1]) + ' ')
                f.write('\n')

    @staticmethod
    def rect_area(rect):
        # compute the area of a rectangle in an image
        if rect.right() - rect.left() < 0 or rect.bottom() - rect.top() < 0:
            return 0
        else:
            return int((rect.right() - rect.left()) * (rect.bottom() - rect.top()))

    @staticmethod
    def rect_center(rect):
        # compute the center of a rectangle in an image
        return int((rect.left() + rect.right()) / 2), int((rect.top() + rect.bottom()) / 2)

    @staticmethod
    def dist(p1, p2):
        # compute the distance of two points
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    def is_stagnant(self, old_rect):
        # check if an obejct is stagnant
        return rect_overlap_rate(old_rect, self.rect) > 0.8 and self.dist(self.center[-1], self.center[-2]) < 5

    def display_rect(self, frame_img, color=(0, 255, 0)):
        # display number and center coordiates of a moving object
        cv2.rectangle(frame_img, (self.rect.left(), self.rect.top()), (self.rect.right(), self.rect.bottom()), color, 2)
        # print("Obj {} at {}".format(self.id, self.center))
        loc = (int(self.rect.left()), int(self.rect.top() - 10))
        txt = self.id
        cv2.putText(frame_img, txt, loc, cv2.FONT_HERSHEY_SIMPLEX, .5, color, 1)


def rect_overlap_rate(rect1, rect2):
    """
    compute the overlap ratio of two rectangles
    :return: overlap ratio = overlap area / area of the smaller rectangle
    """
    [left, right, top, bottom] = zip(rect1.to_list(), rect2.to_list())
    area1 = Obj.rect_area(rect1)
    area2 = Obj.rect_area(rect2)
    overlap_area = Obj.rect_area(Rect(max(left), min(right), max(top), min(bottom)))
    if overlap_area < 0:
        return 0
    if min([area1, area2]) == 0:
        return 1
    else:
        return overlap_area / min([area1, area2])


def is_out_roi(overall_roi, rect):
    """
    check if the object leaves the region of interest
    """
    center = Obj.rect_center(rect)
    return overall_roi[center[1]][center[0]] < 128 or rect.left() < 10 or rect.right() > 1910 \
           or rect.top() < 10 or rect.bottom() > 1070


def object_track(filename, train_frame=600, skip_frame=0, write=False, save_video=False):
    """
    Main method to track moving object
    :param filename: video file
    :param train_frame: frames used to train model
    :param skip_frame: frames to be skipped at the begining of the video
    :param write: write the result or not
    :param save_video: save the tracking video or not
    """

    global tracker_list, tracking_objs

    no_suffix_path = '.'.join(filename.split('.')[:-1])
    overall_roi = cv2.imread(no_suffix_path + '_roi.jpg', cv2.IMREAD_GRAYSCALE)  # set the region of interest
    output_file = no_suffix_path + '_traj.txt'
    if write:
        with open(output_file, 'w') as f: f.write('')  # clear output file
    cap = cv2.VideoCapture(filename)
    _, frame = cap.read()
    # MOG background extractor
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    bg_subtractor.setHistory(train_frame)
    bg_subtractor.setShadowThreshold(0.5)
    bg_subtractor.setShadowValue(127)
    # bg_subtractor.setVarThresholdGen(9)
    bg_subtractor.setVarThreshold(9)
    bg_subtractor.setDetectShadows(True)

    # initialize video window
    cv2.namedWindow('new_frame', 0)
    # cv2.namedWindow('mask', 0)
    # parameters for saving video 3-width，4-hight，5-frames in a second

    out_num = 1
    if save_video:
        out = cv2.VideoWriter('%s_%d.avi' % (no_suffix_path, out_num), 1, 10, (int(cap.get(3)), int(cap.get(4))))
    while (True):
        _, frame = cap.read()
        if frame is None:
            break
        frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)
        if frame_num < skip_frame or frame_num % frame_step != 0:
            continue  # skip frames
        mask_fg = bg_subtractor.apply(frame, 0.01)  # extract frontground
        mask_fg = cv2.medianBlur(mask_fg, 9)  # mean filter
        mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_DILATE,
                                   kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4)))  # morphology dilating
        # Binarization
        mask_fg[mask_fg > 128] = 255
        mask_fg[mask_fg < 128] = 0

        # separate conneted region into independent shapes
        mask_fg, contours, hierarchy = cv2.findContours(mask_fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask_fg = cv2.bitwise_and(mask_fg, overall_roi)

        if frame_num < train_frame + skip_frame:
            print('Frame: ', str(frame_num), '\ttraining background')
            cv2.imshow('new_frame', frame)
            continue

        # divide and save videos in pieces
        if save_video and frame_num > 2000 * out_num:
            out_num += 1
            out.release()
            out = cv2.VideoWriter('%s_%d.avi' % (no_suffix_path, out_num), 1, 10, (int(cap.get(3)), int(cap.get(4))))

        print('Frame', frame_num, end='\t')
        for i in range(len(tracker_list) - 1, -1, -1):
            tracker_list[i].update(frame)  # update tracker
            rect = tracker_list[i].get_position()
            old_rect = copy.deepcopy(tracking_objs[i].rect)
            tracking_objs[i].update(frame_num, (rect.left(), rect.right(), rect.top(), rect.bottom()))
            new_rect = tracking_objs[i].rect
            center = tracking_objs[i].center[-1]

            if is_out_roi(overall_roi, new_rect) or tracking_objs[i].is_stagnant(old_rect):
                # check if current obejct leaves region of interest
                tracking_objs[i].write(output_file)
                del tracking_objs[i]
                del tracker_list[i]
                continue
            tracking_objs[i].display_rect(frame)

        for idx in range(len(contours)):
            # travers all the contours to find untracked objects
            cont_s = contours[idx]
            area = cv2.contourArea(cont_s)
            if area < 200:  # ingore small contours which might be noise
                continue

            x, y, w, h = cv2.boundingRect(cont_s)  # get the wrapper rectangle
            rect1 = Rect(x, x + w, y, y + h)
            is_tracking = False
            for tracker in tracker_list:
                rect2 = tracker.get_position()
                rect2 = Rect(rect2.left(), rect2.right(), rect2.top(), rect2.bottom())
                if rect_overlap_rate(rect1, rect2) > 0:
                    # positive overlapping ratio means the object is being tracked
                    is_tracking = True
                    break

            if not is_tracking and not is_out_roi(overall_roi, rect1):
                # generate new tracker
                tracker_list.append(dlib.correlation_tracker())
                tracker_list[-1].start_track(frame,
                                             dlib.rectangle(rect1.left(), rect1.top(), rect1.right(), rect1.bottom()))
                # add new object
                tracking_objs.append(Obj('a', frame_num, rect1))
                tracking_objs[-1].display_rect(frame, (0, 0, 255))

        if (cv2.waitKey(10) == ord('p')):
            # select objects manually
            points = run(frame, multi=True)
            for j in range(len(points)):
                tracker_list.append(dlib.correlation_tracker())
                tracker_list[-1].start_track(frame, dlib.rectangle(*points[j]))
                rect = tracker_list[-1].get_position()
                rect = Rect(rect.left(), rect.right(), rect.top(), rect.bottom())
                tracking_objs.append(Obj('m', frame_num, rect))
                tracking_objs[-1].display_rect(frame, (255, 0, 0))
                for i in range(len(tracking_objs) - 2, -1, -1):
                    # remove the manually selected objects
                    if rect_overlap_rate(tracking_objs[i].rect, rect) > 0.8:
                        del tracking_objs[i]
                        del tracker_list[i]
                        continue

        print('tracking:', len(tracking_objs), 'objects')
        if save_video:
            out.write(frame)
        cv2.imshow('new_frame', frame)
        cv2.imshow('mask', mask_fg)
        if cv2.waitKey(1) == '27':
            continue
    out.release()


def frame_cut(filename):
    """
    save the first frame
    """
    cap = cv2.VideoCapture(filename)
    _, frame = cap.read()
    output = filename.split('/')[-1][: -4]
    path = "/".join(filename.split('/')[:-2])
    cv2.imwrite("%s/%s/%s.jpg" % (path, output, output), frame)


class Post_process:
    """
    Process raw data retrieved from real-time video analysis
    """

    def __init__(self, filename, real_coord):
        self.path = "/".join(filename.split('/')[:-1])  # raw data path
        self.real_coord = real_coord
        self.folder_name = self.path.split('/')[-1]  # raw data folder name
        self.img_coord_file = self.path + '/img.txt'  # raw data filename
        self.convert_click = 0
        self.M = []  # transformation matrix

    def mouseclick(self, event, x, y, s, p):
        """
        callback function of clicking paused video
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.convert_click == 4:
                return
            with open(self.img_coord_file, 'a') as f:
                f.write(str(x) + '\t' + str(y) + '\n')
            self.convert_click += 1

    def get_image_points(self):
        """
        Retrieve coordinates of images pixels by clicking one paused video
        Coordinates will be saved in img_coord_file
        """
        video_filename = self.path + '/' + self.folder_name + '.jpg'
        one_frame = cv2.imread(video_filename)
        self.convert_click = 0
        with open(self.img_coord_file, 'w') as f:
            f.write('')
        cv2.namedWindow('input', 0)
        cv2.setMouseCallback("input", self.mouseclick)
        cv2.imshow('input', one_frame)
        cv2.waitKey(0)

    def convert_format(self):
        """
        Convert .txt data to .csv data
        """
        self.get_perspective()
        traj_file = self.path + '/' + self.folder_name + '_traj.txt'

        with open(traj_file, 'r') as f:
            data = f.read().strip().split('\n')
        total_df = pd.DataFrame(columns=['ID', 'Time', 'X', 'Y', 'Vel', 'Length', 'Width', 'Accel'])

        for i in range(0, len(data), 3):
            num = data[i].split()[0]
            bound_coord = [int(coord) for coord in data[i].split()[1:]]
            # four corner points of a rectangle boundary: left-up, right-up, left-down, right-down
            bound_coord = np.array(
                [[bound_coord[0], bound_coord[2]], [bound_coord[1], bound_coord[2]], [bound_coord[0], bound_coord[3]],
                 [bound_coord[1], bound_coord[3]]])
            # corner points after perspective transformation
            bound_coord = np.hstack((bound_coord, np.ones((len(bound_coord), 1))))
            time = [(float(t) / 30) for t in data[i + 1].split()]  # column for time sequence
            track = [int(p) for p in data[i + 2].split()]  # column for trajectory points
            track = np.array(list(zip(track[::2], track[1::2])))
            # trajectory points after perspective transformation
            track = np.hstack((track, np.ones((len(track), 1))))

            # convert image coordinates to real-world coordinates
            real_track = np.dot(self.M, track.T)
            real_track = real_track[:2, :].T
            real_bound = np.dot(self.M, bound_coord.T)

            # convert image length and width to real-world scale
            length = self.cal_dist(real_bound[:2, 0], real_bound[:2, 1])
            width = self.cal_dist(real_bound[:2, 1], real_bound[:2, 2])

            if length < width:
                length, width = width, length

            vel = self.cal_vel(real_track)
            accel = self.cal_accel(vel)
            real_track[0] = self.smooth(real_track[0])
            real_track[1] = self.smooth(real_track[1])
            df = pd.DataFrame(np.hstack((real_track[:-2], vel[:-1], accel)), columns=['X', 'Y', 'Vel', 'Accel'])
            df['ID'] = num
            df['Length'] = length
            df['Width'] = width
            df.insert(0, 'Time', time[:-2])
            df = df.reindex(columns=['ID', 'Time', 'X', 'Y', 'Vel', 'Length', 'Width', 'Accel'])
            total_df = pd.concat([total_df, df], axis=0, ignore_index=True)
        total_df.round(2).to_csv(self.path + '/' + self.folder_name + '_result.csv', index=False)

    def smooth(self, arr):
        """
        :param arr: raw trajectory to be smoothed
        :return: smoothed trajectory
        """
        x = range(0, len(arr))
        poly = np.polyfit(x, arr, 5)
        return np.poly1d(poly)(x)

    def cal_vel(self, real_track):
        """
        :param real_track: real-world trajectory
        :return: speed
        """
        track_diff = real_track[:-1, :2] - real_track[1:, :2]
        vel = np.sum(track_diff ** 2, 1) ** 0.5 * 3.6
        vel = self.smooth(vel)
        return vel.reshape(-1, 1)

    def cal_accel(self, vel):
        """
        :param vel: speed
        :return: acceleration
        """
        vel_diff = vel[:-1] - vel[1:]
        return vel_diff

    def cal_dist(self, point1, point2):
        """
        compute distance between two points
        """
        dist = ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
        return dist / 10

    def get_perspective(self):
        """
        :return: real-world coodinate
        """
        with open(self.img_coord_file, 'r') as f:
            real_points = f.read()
        rps = [int(p) for p in real_points.split()]
        rps = list(zip(rps[::2], rps[1::2]))
        img_points = np.float32(rps)
        real_points = np.float32(self.real_coord)
        self.M = cv2.getPerspectiveTransform(img_points, real_points)
        return self.M


if __name__ == "__main__":
    # video path
    filename = 'G:/ZQC/data/jiaoda/jiaoda.avi'
    # fixed points used to calibrate
    real_coord = [[0, 0], [2550, 0], [2550, -250], [0, -250]]

    # get the background image of the first frame
    # frame_cut(filename)
    # object_track(filename, train_frame= 600, write = True, save_video = True)

    # start tracking
    pp = Post_process(filename, real_coord)
    pp.get_image_points()
    pp.convert_format()
