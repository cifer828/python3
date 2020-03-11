import cv2

# drawing = False
# x1, y1 = -1, -1
# x2, y2 = -1, -1
#
# def draw_circle(event, x, y, flags, param):
#     global x1, y1, x2, y2, drawing
#     if drawing:
#         x1 = min([x1, x])
#         y1 = max([y1, y])
#         x2 = max([x2, x])
#         y2 = min([y2, y])
#     if event == cv2.EVENT_LBUTTONDOWN:
#         drawing = True
#         x1, y1 = x, y                        #按下鼠标左键，用全局变量ix,iy记录下当前坐标点
#         x2, y2 = x, y
#     elif event == cv2.EVENT_LBUTTONUP:
#         if drawing == True:
#             drawing = False                  #鼠标左键抬起，画出矩形框
#
#
# cv2.namedWindow('img')
# cv2.setMouseCallback('img', draw_circle)
# cap = cv2.VideoCapture(0)
# while (True):
#     ret, frame = cap.read()
#     cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
#     cv2.imshow('img', frame)
#     if cv2.waitKey(20) & 0xFF == 27:
#         break
#
# cv2.destroyAllWindows()

cv2.namedWindow('img')
cap = cv2.VideoCapture(0)
while (True):
    ret, frame = cap.read()
    cv2.rectangle(frame, (300,300), (200,200), (255,0,0), 1)
    cv2.imshow('img', frame)
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyAllWindows()