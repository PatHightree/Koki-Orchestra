import math
import numpy as np
import cv2 as cv


class Location:
    initialized = False
    blob_index = -1
    keypoint = object

    def __init__(self):
        self.initialized = False
        self.blob_index = -1
        self.keypoint = None

    def set(self, blob_index, keypoint):
        self.initialized = True
        self.blob_index = blob_index
        self.keypoint = keypoint

    def distance(self, coordinates):
        delta = np.subtract(coordinates, self.keypoint.pt)
        return np.linalg.norm(delta)
