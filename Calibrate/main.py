import os
import random

import cv2
import numpy as np
import time
from datetime import datetime
from datetime import timedelta
from wled import *
from camera import *

leds_init(255)
led_brightness = 100
blur_size = 10
brightness_multiplier = 3


def display_sample():
    global t, sample_index
    if datetime.now() > t + interval:
        if sample_index < samples_count:
            t = datetime.now()
            led_set(samples[sample_index], 0)
            sample_index = sample_index + 1
        if sample_index < samples_count:
            led_set(samples[sample_index], led_brightness)


def display_sample_infinite():
    global t, sample_index
    if datetime.now() > t + interval:
        t = datetime.now()
        led_set(samples[sample_index], 0)
        sample_index = (sample_index + 1) % samples_count
        led_set(samples[sample_index], led_brightness)


def display_sample_random():
    global t, sample_index
    if datetime.now() > t + interval:
        t = datetime.now()
        led_set(sample_index, 0)
        sample_index = random.randrange(64)
        led_set(sample_index, led_brightness)


# list_ports()

capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if (capture.isOpened() == False):
    print("Error opening capture stream or file")
frame_width = int(capture.get(3))
frame_height = int(capture.get(4))
print(f"Video resolution={frame_width}x{frame_height}")

samples = [0, 0 + 7, 63, 63 - 7]
samples_count = len(samples)
sample_index = 0
interval = timedelta(seconds=1)

# Prepare capture
leds_off()
time.sleep(1)
ret, background = capture.read()
if ret:
    cv2.imshow("Background", background)
leds_off()
time.sleep(1)
ret, background = capture.read()
if ret:
    cv2.imshow("Background", background)
background = cv2.blur(background, ksize=(blur_size, blur_size))

# Start capture
led_set(samples[sample_index], led_brightness)
t = datetime.now()

detector = cv2.SimpleBlobDetector_create()


while capture.isOpened():
    display_sample_random()

    ret, frameOrg = capture.read()
    if ret:

        # Blur frame
        frame = cv2.blur(frameOrg, ksize=(blur_size, blur_size))
        cv2.imshow("Blur", frame)

        # Subtract background
        delta = cv2.subtract(frame, background)
        delta = delta * brightness_multiplier
        # delta = delta.astype('uint8')
        cv2.imshow("Delta", delta)

        # Invert image because default blob detection wants black blobs on white background
        delta = ~delta

        keypoints = detector.detect(delta)

        # Draw detected blobs as red circles.
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
        im_with_keypoints = cv2.drawKeypoints(frameOrg, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # Show keypoints
        cv2.imshow("Blobs", im_with_keypoints)

        # Press escape to quit
        if cv2.waitKey(25) & 0xFF == 27:
            break

    else:
        break

capture.release()
cv2.destroyAllWindows()
leds_off()
