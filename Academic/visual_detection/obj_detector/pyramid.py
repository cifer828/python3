"""
图像缩放金字塔
"""
import cv2

def resize(img, scaleFactor):
    """
    img: 待调整图像
    scaleFactor: 尺寸调整因子
    """
    return cv2.resize(img, (int(img.shape[1] * (1 / scaleFactor)), int(img.shape[0] * (1 / scaleFactor))), interpolation=cv2.INTER_AREA)

def pyramid(image, scale=1.5, minSize=(64, 128)):
    """
    minSize: 图像最小尺寸
    """
    yield image

    while True:
        image = resize(image, scale)
        if image.shape[0] < minSize[1] or image.shape[1] < minSize[0]:
            break

    yield image
