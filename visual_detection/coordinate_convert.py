import cv2
import numpy as np

img_coord_file = ''   # 坐标文件名
convert_click = 0   # 坐标转换时点击标定点次数
# M = [] # 坐标转换矩阵

def read_coord(filename):
    """
    读取坐标点，4行，左上开始顺时针
    """
    with open(filename, 'r') as f:
        real_points = f.read()
    rps= [int(p) for p in real_points.split()]
    rps = list(zip(rps[::2], rps[1::2]))
    real_points = np.float32(rps)
    return real_points

def mouseclick(event, x, y, s, p):
    """
    左上角点顺时针点击四个标定点，获取点的图像坐标
    """
    global convert_click
    if event == cv2.EVENT_LBUTTONDOWN:
        if convert_click == 4:
            return
        with open(img_coord_file, 'a') as f:
            f.write(str(x) + '\t' + str(y) + '\n')
        convert_click += 1

def get_image_points(one_frame, filename):
    """
    获取四个标定点图像坐标写入txt
    需左上角开始顺时针点击
    one_frame: 一帧图像
    """
    global convert_click, img_coord_file
    img_coord_file = filename
    convert_click = 0
    with open(filename, 'w') as f:
        f.write('')
    cv2.namedWindow('input', 0)
    cv2.setMouseCallback("input", mouseclick)
    cv2.imshow('input', one_frame)
    cv2.waitKey(0)

def get_convert_mat(filename, param = 0):
    """
    filename: 视频文件
    param: 0 - 使用文件中点标定
           1 - 重新标定
    返回变换矩阵
    """
    global img_coord_file
    sub_filename = filename.split('/')[-1][: -4]
    img_coord_file = 'data/' + sub_filename + '/' + sub_filename + '_img_coord.txt'
    real_coord_file = 'data/'+ sub_filename + '/' + sub_filename + '_real_coord.txt'
    if param == 1:
        capture = cv2.VideoCapture(filename)
        ret, frame = capture.read()
        get_image_points(frame, img_coord_file)
    img_points = read_coord(img_coord_file)
    real_points = read_coord(real_coord_file)
    M = cv2.getPerspectiveTransform(img_points, real_points)
    return M

def coord_convert(img_coord, M):
    """
    四点标定透视转换
    转换矩阵记录在全局变量中
    img_coord: 图像坐标
    return: 真实坐标
    """
    new_img_coord = list(img_coord) + [1]
    new_point = np.dot(M, np.array(new_img_coord).T)
    new_point = new_point * 1.0 / new_point[2]
    return [int(new_point[0]), int(new_point[1])]

def convert_test():
    filename = "D:/文档/研究生/研二/交通行为参数/数据/交叉口视频/1111_4.MOV"
    M = get_convert_mat(filename, 0)
    print(coord_convert([1150, 969], M))
    # dst = cv2.warpPerspective(frame, M, frame.shape[:2])
    # cv2.imshow('output', dst)
    # cv2.waitKey(0)

if __name__ == "__main__":
    # convert_test()
    get_image_points(cv2.imread('D:/jl.png'), filename = 'image.txt')
    # get_image_points(cv2.imread('D:/data/0328_1/0328_1_bg.jpg'), filename = 'image.txt')