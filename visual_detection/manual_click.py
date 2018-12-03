import cv2
from visual_detection.diff_test import Obj, clear_routes_file, write_obj

click_flag = False
frame_num = 0
obj = None

def mouseclick(event, x, y, s, p):
    """
    左上角点顺时针点击四个标定点，获取点的图像坐标
    """
    global click_flag, obj
    if event == cv2.EVENT_LBUTTONDOWN:
        if click_flag:
            obj.update(frame_num, (x, y), 0)
        else:
            obj = Obj(1, frame_num, (x, y), 0)
            click_flag = True

def manual_click(filename):
    global frame_num, click_flag
    sub_filename = filename.split('/')[-1][: -4]
    cap = cv2.VideoCapture(filename)
    click_flag = False
    cv2.namedWindow('input', 0)
    cv2.setMouseCallback("input", mouseclick)
    while(1):
        _, frame = cap.read()
        frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)
        if frame_num % 2 == 0:
            continue
        elif frame_num > 450:
            break
        cv2.putText(frame, str(frame_num), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        cv2.imshow('input', frame)
        cv2.waitKey(0)
    clear_routes_file(sub_filename)
    write_obj(sub_filename, obj)

manual_click('D:/data/left/left.mov')