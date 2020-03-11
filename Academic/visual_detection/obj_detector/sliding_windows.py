import cv2
import numpy as np
from visual_detection.obj_detector.pyramid import pyramid
from visual_detection.obj_detector.non_maximum import non_max_suppression_fast as nms
from visual_detection.obj_detector.detector import Detector
from visual_detection.obj_detector.sliding_window import sliding_window

def in_range(number, test, thresh=0.2):
    return abs(number - test) < thresh

img_path = "C:/Users/zhqch/Documents/code/Python3Projects/visual_detection/input/image.jpg"

ped_detector = Detector('D:\TrainData\Pedestrians64x128')
ped_detector.svm_training()
ped_detector.predict_one(img_path)
svm  = ped_detector.svm
extractor = ped_detector.extract_bow
detect = cv2.xfeatures2d.SIFT_create()


w, h = 64, 128
img = cv2.imread(img_path)

rectangles = []
counter = 1
scaleFactor = 1.25
scale = 1
font = cv2.FONT_HERSHEY_PLAIN

for resized in pyramid(img, scaleFactor,(64, 128)):
    scale = float(img.shape[1]) / float(resized.shape[1])
    for (x, y, roi) in sliding_window(resized, 4, (64, 128)):
    
        if roi.shape[1] != w or roi.shape[0] != h:
            continue

        try:
            bow_features = extractor.compute(roi, detect.detect(roi))
            _, result = svm.predict(bow_features)
            a, res = svm.predict(bow_features, flags=cv2.ml.STAT_MODEL_RAW_OUTPUT | cv2.ml.STAT_MODEL_UPDATE_MODEL)
            print("Class: %d, Score: %f, a: %s" % (result[0][0], res[0][0], res))
            score = res[0][0]
            if result[0][0] == 1:
                if score < -1.0:
                    rx, ry, rx2, ry2 = int(x * scale), int(y * scale), int((x+w) * scale), int((y+h) * scale)
                    rectangles.append([rx, ry, rx2, ry2, abs(score)])
        except:
            pass

        counter += 1

windows = np.array(rectangles)
boxes = nms(windows, 0.25)

for (x, y, x2, y2, score) in boxes:
      print(x, y, x2, y2, score)
      cv2.rectangle(img, (int(x),int(y)),(int(x2), int(y2)),(0, 255, 0), 1)
      cv2.putText(img, "%f" % score, (int(x),int(y)), font, 1, (0, 255, 0))


cv2.namedWindow('img', 0) # 调整窗口大小
cv2.imshow("img", img)
cv2.waitKey(0)
