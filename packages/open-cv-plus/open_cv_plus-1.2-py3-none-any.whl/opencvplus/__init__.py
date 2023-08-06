import cv2
from .Images import __init__


def captureImg(filepath):
    camera = cv2.VideoCapture(0)
    return_value, image = camera.read()
    cv2.imwrite(filepath, image)
    del camera


def blur(image, intensity:tuple):
    blurred = cv2.GaussianBlur(image, intensity, cv2.BORDER_DEFAULT)
    return blurred
