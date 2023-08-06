import cv2 as cv


def captureImage(filenameWithoutDotPng):
    camera = cv.VideoCapture(0)
    return_value, image = camera.read()
    cv.imwrite(f'{filenameWithoutDotPng}.png', image)
    del camera
