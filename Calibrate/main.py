import asyncio
import time
import cv2 as cv
import numpy as np
from wled import *
import dearpygui.dearpygui as dpg

display_brightness = 100
led_value = 70
led_count = 64
blur_size = 10
capture_brightness_multiplier = 5
delay = 100
blobs = []
image_tag = "image"
background_tag = "background"
sample_tag = "sample"
delta_tag = "delta"
blobs_tag = "blobs"
restart_tag = "restart"
output_tag = "output"


def to_dpg(cv_frame):
    data = np.flip(cv_frame, 2)  # because the camera data comes in as BGR and we need RGB
    data = data.ravel()  # flatten camera data to a 1 d stricture
    data = np.asfarray(data, dtype='f')  # change data type to 32bit floats
    return np.true_divide(data, 255.0)  # normalize image data to prepare for GPU


def to_dpg_tag(cv_frame, tag):
    texture_data = to_dpg(cv_frame)
    dpg.set_value(tag, texture_data)


def calibrate():
    pass


def switch_output(sender, data):
    dpg.configure_item(image_tag, texture_tag=dpg.get_value(output_tag))


async def main():
    leds_init(display_brightness)
    leds_off()

    dpg.create_context()
    dpg.create_viewport(title='Custom Title', width=1920, height=1080)
    dpg.setup_dearpygui()

    vid = cv.VideoCapture(1, cv.CAP_DSHOW)
    start = time.time()
    while time.time() < start + 2:
        ret, test = vid.read()
    texture_data = to_dpg(test)

    # image size or you can get this from image shape
    frame_width = int(vid.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(vid.get(cv.CAP_PROP_FRAME_HEIGHT))
    video_fps = int(vid.get(cv.CAP_PROP_FPS))
    print(f"Video resolution={frame_width}x{frame_height}@{video_fps}")

    with dpg.texture_registry(show=True):
        dpg.add_raw_texture(test.shape[1], test.shape[0], texture_data, format=dpg.mvFormat_Float_rgb, tag=background_tag, label=background_tag)
        dpg.add_raw_texture(test.shape[1], test.shape[0], texture_data, format=dpg.mvFormat_Float_rgb, tag=sample_tag, label=sample_tag)
        dpg.add_raw_texture(test.shape[1], test.shape[0], texture_data, format=dpg.mvFormat_Float_rgb, tag=delta_tag, label=delta_tag)
        dpg.add_raw_texture(test.shape[1], test.shape[0], texture_data, format=dpg.mvFormat_Float_rgb, tag=blobs_tag, label=blobs_tag)
    with dpg.window(label="Koki'orchestra"):
        dpg.add_slider_int(label="Capture brightness multiplier", tag="capture_brightness_multiplier")
        dpg.configure_item("capture_brightness_multiplier", min_value=1)
        dpg.configure_item("capture_brightness_multiplier", max_value=10)
        # dpg.add_button(label="Restart calibration", tag=restart_tag, callback=calibrate)
        dpg.add_radio_button(tag=output_tag, items=[blobs_tag, background_tag, delta_tag], default_value=1, callback=switch_output, horizontal=True)
        dpg.add_image(tag=image_tag, texture_tag=blobs_tag, show=True)

    dpg.set_value("capture_brightness_multiplier", capture_brightness_multiplier)
    dpg.show_metrics()
    dpg.show_viewport(maximized=True)

    ret, background = vid.read()
    background_blur = cv.blur(background, ksize=(blur_size, blur_size))
    detector = cv.SimpleBlobDetector_create()
    led_index = 0
    while dpg.is_dearpygui_running():
        led_set(led_index, 0)
        led_index = (led_index + 1) % led_count
        led_set(led_index, led_value)

        time.sleep(0.1)
        # await asyncio.sleep(delay)

        ret, sample = vid.read()
        to_dpg_tag(sample, sample_tag)

        sample_blur = cv.blur(sample, ksize=(blur_size, blur_size))
        delta = cv.subtract(sample_blur, background_blur)
        delta = delta * dpg.get_value("capture_brightness_multiplier")
        # delta = ~delta
        to_dpg_tag(delta, delta_tag)

        keypoints = detector.detect(delta)
        if len(keypoints) == 1:
            blobs.append(keypoints[0])
        im_with_keypoints = cv.drawKeypoints(sample, blobs, np.array([]), (0, 0, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        to_dpg_tag(im_with_keypoints, blobs_tag)

        dpg.render_dearpygui_frame()

        # if cv.waitKey(25) & 0xFF == 27:
        #     break

    vid.release()
    dpg.destroy_context()
    leds_off()


asyncio.run(main())
