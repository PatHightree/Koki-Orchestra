import dearpygui.dearpygui as dpg
import cv2 as cv
import numpy as np
from wled import *

display_brightness = 100
led_value = 70
led_count = 64
led_index = 0
blur_size = 10
capture_brightness_multiplier = 5
delay = 100
background_tag = "background"
sample_tag = "sample"
delta_tag = "delta"
blobs_tag = "blobs"


def to_dpg(cv_frame, tag):
    data = np.flip(cv_frame, 2)
    data = data.ravel()
    data = np.asfarray(data, dtype='f')
    texture_data = np.true_divide(data, 255.0)
    dpg.set_value(tag, texture_data)


leds_init(display_brightness)
leds_off()

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=1920, height=1080)
dpg.setup_dearpygui()

vid = cv.VideoCapture(1, cv.CAP_DSHOW)
vid.read()
ret, background = vid.read()
background_blur = cv.blur(background, ksize=(blur_size, blur_size))

# image size or you can get this from image shape
frame_width = int(vid.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(vid.get(cv.CAP_PROP_FRAME_HEIGHT))
video_fps = int(vid.get(cv.CAP_PROP_FPS))
print(f"Video resolution={frame_width}x{frame_height}@{video_fps}")

data = np.flip(background_blur, 2)  # because the camera data comes in as BGR and we need RGB
data = data.ravel()  # flatten camera data to a 1 d stricture
data = np.asfarray(data, dtype='f')  # change data type to 32bit floats
texture_data = np.true_divide(data, 255.0)  # normalize image data to prepare for GPU

with dpg.texture_registry(show=True):
    dpg.add_raw_texture(background.shape[1], background.shape[0], texture_data, tag=background_tag, format=dpg.mvFormat_Float_rgb, label=background_tag)
    dpg.add_raw_texture(background.shape[1], background.shape[0], texture_data, tag=sample_tag, format=dpg.mvFormat_Float_rgb, label=sample_tag)
    dpg.add_raw_texture(background.shape[1], background.shape[0], texture_data, tag=delta_tag, format=dpg.mvFormat_Float_rgb, label=delta_tag)
    dpg.add_raw_texture(background.shape[1], background.shape[0], texture_data, tag=blobs_tag, format=dpg.mvFormat_Float_rgb, label=blobs_tag)

with dpg.window(label="Koki'orchestra"):
    dpg.add_slider_int(label="Capture brightness multiplier", tag="capture_brightness_multiplier", default_value=capture_brightness_multiplier)
    dpg.configure_item("capture_brightness_multiplier", min_value=1)
    dpg.configure_item("capture_brightness_multiplier", max_value=10)
    dpg.add_image(blobs_tag)

detector = cv.SimpleBlobDetector_create()

dpg.show_metrics()
dpg.show_viewport(maximized=True)
while dpg.is_dearpygui_running():
    led_set(led_index, 0)
    led_index = (led_index + 1) % led_count
    led_set(led_index, led_value)

    if cv.waitKey(delay) & 0xFF == 27:
        break

    ret, sample = vid.read()
    to_dpg(sample, sample_tag)

    sample_blur = cv.blur(sample, ksize=(blur_size, blur_size))
    delta = cv.subtract(sample_blur, background_blur)
    delta = delta * dpg.get_value("capture_brightness_multiplier")
    # delta = ~delta
    to_dpg(delta, delta_tag)

    keypoints = detector.detect(delta)
    im_with_keypoints = cv.drawKeypoints(sample, keypoints, np.array([]), (0, 0, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    to_dpg(im_with_keypoints, blobs_tag)

    dpg.render_dearpygui_frame()

vid.release()
dpg.destroy_context()
leds_off()