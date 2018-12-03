#!/usr/bin/env python

'''
Lucas-Kanade tracker
====================

Lucas-Kanade sparse optical flow demo. Uses goodFeaturesToTrack
for track initialization and back-tracking for match verification
between frames.

Usage
-----
lk_track.py [<video_source>]


Keys
----
ESC - exit
'''

import cv2
import numpy as np
import video
from visual_detection.common import draw_str

# roi_mask = cv2.imread('data/1111_3_roi.jpg')
lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.2,
                       minDistance = 7,
                       blockSize = 7 )

class App:
    def __init__(self, video_src):
        self.track_len = 1000
        self.detect_interval = 2
        self.tracks = []
        self.cam = video.create_capture(video_src)
        self.frame_idx = 0

    def run(self):
        # bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        # bg_subtractor.setHistory(500)
        # bg_subtractor.setVarThreshold(25)
        # bg_subtractor.setDetectShadows(True)
        cap_mask = cv2.VideoCapture('E:/1111_4_1_mask.avi')
        while(True):
            ret, frame = self.cam.read()
            vis = frame.copy()
            # frame = cv2.bitwise_and(frame, roi_mask)
            # mask_fg = bg_subtractor.apply(frame, 0.01)        # 提取前景
            _, mask_fg = cap_mask.read()
            mask_fg = cv2.cvtColor(mask_fg, cv2.COLOR_BGR2GRAY)
            mask_fg[mask_fg > 128 ] = 255
            mask_fg[mask_fg < 128 ] = 0
            # mask_fg = cv2.medianBlur(mask_fg, 7)    # 中值滤波
            # mask_fg = cv2.morphologyEx(mask_fg, cv2.MORPH_DILATE, kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # frame_gray = cv2.bitwise_and(frame_gray, mask_fg)

            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                d2 = abs(p0-p1).reshape(-1, 2).max(-1)
                good = d < 1
                good2 = d2 < 0.05
                new_tracks = []
                for tr, (x, y), good_flag, good2_flag in zip(self.tracks, p1.reshape(-1, 2), good, good2):
                    if not good_flag or good2_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                    cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                self.tracks = new_tracks
                cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
                draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))

            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv2.circle(mask_fg, (x, y), 5, 0, -1)
                p = cv2.goodFeaturesToTrack(frame_gray, mask = mask_fg, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])


            self.frame_idx += 1
            self.prev_gray = frame_gray
            cv2.imshow('lk_track', vis)

            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break

def main():
    try: video_src = 'D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/1111_4_1.avi'
    except: video_src = 0

    print(__doc__)
    App(video_src).run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
