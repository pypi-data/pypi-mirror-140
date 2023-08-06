import cv2


def bgr2Grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray


def grayscale2Bgr(image):
    return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)


def bgr2Hsv(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


def hsv2Bgr(image):
    return cv2.cvtColor(image, cv2.COLOR_HSV2BGR)


def bgr2Rgb(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def rgb2Bgr(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def grayscale2Hsv(image):
    bgr = grayscale2Bgr(image)
    return bgr2Hsv(bgr)


def hsv2Grayscale(image):
    bgr = hsv2Bgr(image)
    return bgr2Grayscale(bgr)


def grayscale2Rgb(image):
    bgr = grayscale2Bgr(image)
    return bgr2Rgb(bgr)


def rgb2Grayscale(image):
    bgr = rgb2Bgr(image)
    return bgr2Grayscale(bgr)
