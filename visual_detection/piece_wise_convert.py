#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/4/2 23:35
# @Author  : Cifer
# @File    : piece_wise_convert.py

###################################################################################################
# 视频分段标注脚本  required_package:  cv2, pandas
# 1. 将待处理视频转换为 1920 x 1080 / 30帧的格式
# 2. 将视频文件、_result.csv 和该脚本放在同一路径下
# 3. 修改Piece_wise(视频文件路径，待分割的时刻列表(单位s, 第一位必须为1))。
#     分割时刻t表示t到t+1时间内的坐标按t时刻图像进行标定。
#     如xxx.avi视频在第10s, 20s，30s进行分割，则输入
#     Piece_wise(‘xxx.avi’，[1,10,20,30])
# 4. 在弹出的画面中，依此点击4个标定点，之后按空格进入下一标定帧，按相同顺序点击该帧的4个标定点，直至标定完成。
#    第一个标定帧为视频起始帧，后续每个标定帧为脚本输入的分割时刻所在帧。
#    如Piece_wise(‘xxx.avi’，[1,10,20,30]) 会弹出四次标定画面，即第1，10，20，30帧的图像。
# 5. 原文件夹下生成xxx_new_traj.csv文件，即为分段标定结果
#####################################################################################################

import cv2
import numpy as np
import pandas as pd
import pickle as pk

class Piece_wise:
    def __init__(self, video_file, time_piece_list, real_coord=[[]]):
        self.click = 0
        self.M_list = []
        self.points_list = []
        self.current_points = []
        self.current_frame = np.array([])
        self.real_coord = real_coord
        self.video_file = video_file
        self.time_piece_list = [t for t in time_piece_list]

    def __mouse_click(self, event, x, y, _, __):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.click >= 4:
                self.points_list = []
                return
            else:
                cv2.putText(self.current_frame, '(%d, %d)' % (x, y), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, [255, 255, 255], 1)
                cv2.circle(self.current_frame, (x, y), 3, (0, 0, 255), 5)
                cv2.imshow('select four calibration points', self.current_frame)
                self.current_points.append((x,y))
                self.convert_click += 1

    def read_coord(self, filename):
        with open(filename, 'r') as f:
            real_points = f.read()
        rps = [int(p) for p in real_points.split()]
        rps = list(zip(rps[::2], rps[1::2]))
        real_points = np.float32(rps)
        return real_points

    def get_image_points(self):
        self.convert_click = 0
        cv2.namedWindow('select four calibration points', 0)
        cap = cv2.VideoCapture(self.video_file)
        for time_piece in self.time_piece_list:
            while(cap.get(cv2.CAP_PROP_POS_FRAMES) < time_piece * 30):
                _, self.current_frame = cap.read()
            cv2.putText(self.current_frame, 'Time: ' + str(round(time_piece, 1)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, [255, 255, 255], 2)
            cv2.setMouseCallback("select four calibration points", self.__mouse_click)
            cv2.imshow('select four calibration points', self.current_frame)
            cv2.waitKey(0)
            self.points_list.append(self.current_points)
            self.get_convert_mat(self.points_list[0], self.current_points)
            # if cv2.waitKey(0) == '27':
            #     continue
        with open('M.pk', 'wb') as f:
            pk.dump(self.M_list, f)
        cv2.destroyAllWindows()

    def get_convert_mat(self, init_points, current_points):
        M = cv2.getPerspectiveTransform(np.array(init_points, dtype='float32'), np.array(current_points, dtype='float32'))
        self.M_list.append(M)
        self.current_points = []
        return M

    def replace_coord(self):
        with open('M.pk', 'rb') as f:
            self.M_list = pk.load(f)
        result_file = self.video_file.split('.')[0] + '_result.csv'
        df = pd.read_csv(result_file)
        df.sort_values(by='Time', inplace=True)
        for idx, time_piece in enumerate(self.time_piece_list[1:]):
            coord_df = df.loc[df['Time'] > time_piece].loc[:, ['X', 'Y']]
            df.loc[df['Time'] > time_piece, ['X', 'Y']] = self.coord_convert(coord_df, self.M_list[idx + 1])
        df.sort_values(by=['ID','Time']).to_csv(self.video_file.split('.')[0] + '_new_result.csv', index = 0)

    def coord_convert(self, raw_coord_df, M):
        raw_coord_df['z'] = 1
        new_point = np.dot(M, np.array(raw_coord_df.values).T)
        new_point = new_point * 1.0 / new_point[2]
        return pd.DataFrame(new_point[:2,:].T, columns=['X', 'Y'], index= raw_coord_df.index).astype(int)

if __name__ == "__main__":
    pw = Piece_wise('data\\jiaoda\\jiaoda.avi', [1, 30])
    pw.get_image_points()
    pw.replace_coord()
