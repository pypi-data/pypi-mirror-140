import cv2
import numpy as np


class ChannelChanger:
    def __init__(self, img):
        self.img = img
        self.b, self.g, self.r = cv2.split(img)

    def turnToRed(self):
        blank = np.zeros(self.img.shape[:2], dtype='uint8')
        return cv2.merge([blank, blank, self.r])

    def turnToGreen(self):
        blank = np.zeros(self.img.shape[:2], dtype='uint8')
        return cv2.merge([blank, self.g, blank])

    def turnToBlue(self):
        blank = np.zeros(self.img.shape[:2], dtype='uint8')
        return cv2.merge([self.b, blank, blank])
