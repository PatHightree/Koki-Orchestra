import os
import random

import cv2
import numpy as np
from timeit import default_timer as timer
from wled import *
from camera import *

display_brightness = 100
led_value = 70
led_count = 64
led_index = 0
blur_size = 10
capture_brightness_multiplier = 2


def display_sequential():
    global led_index
    led_set(led_index, 0)
    led_index = (led_index + 1) % led_count
    led_set(led_index, led_value)


def capture_background():
    print("Background {}", timer())
    ret, background = capture.read()
    while not ret:
        pass
    background = cv2.blur(background, ksize=(blur_size, blur_size))
    return background


def capture_sample():
    print("Sample {}", timer())
    ret, frame = capture.read()
    while not ret:
        pass
    frame_blur = cv2.blur(frame, ksize=(blur_size, blur_size))
    return frame, frame_blur


capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not capture.isOpened():
    print("Error opening capture stream or file")
frame_width = int(capture.get(3))
frame_height = int(capture.get(4))
print(f"Video resolution={frame_width}x{frame_height}")

# capture background twice to let camera sensitivity accommodate
leds_init(display_brightness)
leds_off()
cv2.waitKey(100)
capture_background()
cv2.waitKey(100)
background_blur = capture_background()
cv2.imshow("Background", background_blur)
cv2.moveWindow("Background", 0, 0)

detector = cv2.SimpleBlobDetector_create()

delay = 100
while capture.isOpened():
    led_set(led_index, 0)
    led_index = (led_index + 1) % led_count
    led_set(led_index, led_value)

    if cv2.waitKey(delay) & 0xFF == 27:
        break

    sample, sample_blur = capture_sample()
    cv2.imshow("Sample", sample_blur)
    cv2.moveWindow("Sample", frame_width, 0)
    led_set(led_index, led_value)

    # Subtract background
    delta = cv2.subtract(sample_blur, background_blur)
    delta = delta * capture_brightness_multiplier
    cv2.imshow("Delta", delta)
    cv2.moveWindow("Delta", 0, frame_height)

    # Invert image because default blob detection wants black blobs on white background
    delta = ~delta

    keypoints = detector.detect(delta)
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(sample, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # Show keypoints
    cv2.imshow("Blobs", im_with_keypoints)
    cv2.moveWindow("Blobs", frame_width, frame_height)

capture.release()
cv2.destroyAllWindows()
leds_off()
