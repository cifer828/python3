import numpy as np
import cv2

drawing = False
selectedRect = 0
x1, y1 = -1, -1
x2, y2 = -1, -1

def draw_rect(event, x, y, flags, param):
    global x1, y1, x2, y2, drawing, selectedRect
    if drawing:
        x1 = min([x1, x])
        y1 = min([y1, y])
        x2 = max([x2, x])
        y2 = max([y2, y])
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x1, y1 = x, y                        #按下鼠标左键，用全局变量ix,iy记录下当前坐标点
        x2, y2 = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        if drawing == True:
            drawing = False                  #鼠标左键抬起，画出矩形框
        selectedRect = 1

cap = cv2.VideoCapture(0)
# setup initial location of window
cv2.namedWindow('img')
cv2.setMouseCallback('img', draw_rect)

# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 1 )

while(1):
    ret ,frame = cap.read()

    if ret == True:
        if selectedRect == 0:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
            cv2.imshow('img', frame)
            if cv2.waitKey(20) & 0xFF == 27:
                break
        else:
            # mark the ROI
            r,h,c,w = y1, abs(y2-y1), x1, abs(x2-x1)
            # r,h,c,w = 10, 200, 10, 200
            # wrap in a tuple
            track_window = (c,r,w,h)

            # extract the ROI for tracking
            roi = frame[r:r+h, c:c+w]
            # switch to HSV
            hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            # create a mask with upper and lower boundaries of colors you want to track
            mask = cv2.inRange(hsv_roi, np.array((100., 30.,32.)), np.array((180.,120.,255.)))
            # calculate histograms of roi
            roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
            cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
            print(dst)
            # apply meanshift to get the new location
            ret, track_window = cv2.meanShift(dst, track_window, term_crit)

            # Draw it on image
            x,y,w,h = track_window
            img2 = cv2.rectangle(frame, (x,y), (x+w,y+h), 255,2)
            cv2.imshow('img',img2)

            k = cv2.waitKey(60) & 0xff
            if k == 27:
                break

    else:
        break

cv2.destroyAllWindows()
cap.release()
