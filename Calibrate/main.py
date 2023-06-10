import asyncio
import threading

from wled import *
from video import *
from gui import *

camera_brightness_multiplier = 5
display_brightness = 100
led_value = 70
led_count = 64
blur_size = 10
delay = 100
blobs = []
calibrate_stop = False
calibrate_running = False


def start_calibrate_thread(sender, app_data, user_data):
    global calibrate_running, calibrate_stop
    dpg.configure_item(start_tag, label="Start calibration" if calibrate_running else "Stop calibration")
    dpg.configure_item(output_radio_tag, show=False if calibrate_running else True)
    dpg.configure_item(brightness_slider_tag, show=False if calibrate_running else True)
    if calibrate_running:
        calibrate_stop = True
    else:
        threading.Thread(target=calibrate, daemon=True, args=(user_data,)).start()


def calibrate(vid):
    global calibrate_running, calibrate_stop
    calibrate_running = True
    ret, background = vid.read()
    background_blur = cv.blur(background, ksize=(blur_size, blur_size))
    detector = cv.SimpleBlobDetector_create()
    led_index = -1
    blobs.clear()
    calibrate_stop = False
    while not calibrate_stop:
        led_index = sample_led(background_blur, detector, led_index, vid)
    calibrate_running = False
    leds_off()


async def main():
    global calibrate_stop
    leds_init(display_brightness)
    leds_off()

    vid, test, texture_data = init_video()
    init_gui(vid, test, texture_data, switch_output, start_calibrate_thread, camera_brightness_multiplier)

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    calibrate_stop = True
    while calibrate_running:
        time.sleep(0.1)
    vid.release()
    dpg.destroy_context()
    leds_off()


def sample_led(background_blur, detector, led_index, vid):
    led_set(led_index, 0)
    led_index = (led_index + 1) % led_count
    led_set(led_index, led_value)

    time.sleep(0.1)

    ret, sample = vid.read()
    to_dpg_tag(sample, sample_tag)
    sample_blur = cv.blur(sample, ksize=(blur_size, blur_size))
    delta = cv.subtract(sample_blur, background_blur)
    delta = delta * dpg.get_value(brightness_slider_tag)
    # delta = ~delta
    to_dpg_tag(delta, delta_tag)
    keypoints = detector.detect(delta)
    if len(keypoints) == 1:
        blobs.append(keypoints[0])
    else:
        border_width = 10
        sample = cv.rectangle(
            sample,
            (0, 0),
            (sample.shape[1] - 1, sample.shape[0] - 1),
            (0, 0, 255),  # (B, G, R)
            border_width
        )
        led_index -= 1
    im_with_keypoints = cv.drawKeypoints(sample, blobs, np.array([]), (0, 0, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    to_dpg_tag(im_with_keypoints, blobs_tag)
    return led_index


asyncio.run(main())
