def sliding_window(image, stepSize, windowSize):
    """
    滑动窗口函数，从左至右，从上至下
    :param stepSize: 滑动步长
    :param windowSize: 窗口尺寸
    :return:
    """
    for y in range(0, image.shape[0], stepSize):
        for x in range(0, image.shape[1], stepSize):
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])
