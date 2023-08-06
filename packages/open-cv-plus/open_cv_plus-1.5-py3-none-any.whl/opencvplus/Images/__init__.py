import cv2


def captureImg(filepath):
    camera = cv2.VideoCapture(0)
    return_value, image = camera.read()
    cv2.imwrite(filepath, image)
    del camera


def getImage():
    camera = cv2.VideoCapture(0)
    return_value, image = camera.read()
    del camera
    return image


def blur(image, intensity: tuple):
    blurred = cv2.GaussianBlur(image, intensity, cv2.BORDER_DEFAULT)
    return blurred


def blur2(image, intensity: int):
    blurred = cv2.GaussianBlur(image, (intensity, intensity), cv2.BORDER_DEFAULT)
    return blurred
