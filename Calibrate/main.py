import asyncio
import threading

from wled import *
from video import *
from gui import *
from location import *

camera_brightness_multiplier = 5
display_brightness = 100
calibrate_value = 70
blur_size = 10
delay = 100
retries = 5
blobs = []
locations = []
calibrate_running = False
calibrate_stop = False
orchestrate_running = False
orchestrate_stop = False


def start_orchestrate_thread(sender, app_data, user_data):
    global orchestrate_running, orchestrate_stop

    dpg.configure_item(orchestrate_button_tag, label="Start orchestrating" if orchestrate_running else "Stop orchestrating")
    if orchestrate_running:
        orchestrate_stop = True
    else:
        threading.Thread(target=orchestrate, daemon=True, args=(user_data,)).start()


def orchestrate(vid):
    global orchestrate_running, orchestrate_stop

    keypoints = []
    for index, location in enumerate(locations):
        keypoints.append(location.keypoint)

    orchestrate_stop = False
    orchestrate_running = True
    leds_off()
    values = []
    image_pos = dpg.get_item_pos(image_tag)

    # dpg.show_debug()
    # print(f"Image pos {dpg.get_item_pos(image_tag)}")
    # print(f"Mouse pos {dpg.get_mouse_pos()}")
    # print(f"mouse {dpg.get_mouse_pos()} image min {dpg.get_item_rect_min(image_tag)} max {dpg.get_item_rect_max(image_tag)} size {dpg.get_item_rect_size(image_tag)}")
    while not orchestrate_stop:
        mouse_pos_relative = np.subtract(dpg.get_mouse_pos(), image_pos)
        values.clear()
        for index, location in enumerate(locations):
            if location.initialized:
                d = location.distance(mouse_pos_relative)
                diameter = 50
                value = int(led_value * np.clip((1 - d / diameter), 0, 1))
                values.append([index, [value, value, value]])
            else:
                values.append([index, [0, 0, 0]])
        leds_set_rle(values)

        ret, blobs = vid.read()
        # blobs = cv.drawKeypoints(blobs, keypoints, np.array([]), (0, 0, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        to_dpg_tag(blobs, blobs_tag)
    orchestrate_running = False


def start_calibrate_thread(sender, app_data, user_data):
    global calibrate_running, calibrate_stop
    dpg.configure_item(calibrate_button_tag, label="Start calibration" if calibrate_running else "Stop calibration")
    # dpg.configure_item(output_radio_tag, show=False if calibrate_running else True)
    # dpg.configure_item(brightness_slider_tag, show=False if calibrate_running else True)
    if calibrate_running:
        calibrate_stop = True
    else:
        threading.Thread(target=calibrate, daemon=True, args=(user_data,)).start()


def calibrate(vid):
    global calibrate_running, calibrate_stop
    ret, background = vid.read()
    background_blur = cv.blur(background, ksize=(blur_size, blur_size))
    to_dpg_tag(background_blur, background_tag)

    detector = cv.SimpleBlobDetector_create()
    led_index = 0
    blobs.clear()
    locations.clear()
    for l in range(led_count):
        locations.append(Location())

    calibrate_running = True
    calibrate_stop = False
    calibrated = 0
    while not calibrate_stop and calibrated < led_count:
        sample_led(background_blur, detector, led_index, vid)
        if locations[led_index].initialized:
            calibrated += 1
        else:
            calibrated = 0
        led_index = (led_index + 1) % led_count
    calibrate_running = False
    leds_off()
    time.sleep(0.1)

    ret, sample = vid.read()
    ret, sample = vid.read()
    ret, sample = vid.read()
    im_with_keypoints = cv.drawKeypoints(sample, blobs, np.array([]), (0, 0, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    to_dpg_tag(im_with_keypoints, blobs_tag)
    dpg.configure_item(calibrate_button_tag, label="Start calibration")


def sample_led(background_blur, detector, led_index, vid):
    if locations[led_index].initialized:
        return True

    leds_off()
    led_set(led_index, calibrate_value)

    attempts = 1
    success = False
    while attempts < retries and not success:
        # when using sleep(), the first led isn't captured in time and the locations array gets misaligned
        time.sleep(0.05)
        # recording multiple frames does yield correct results
        ret, sample = vid.read()
        ret, sample = vid.read()
        ret, sample = vid.read()

        to_dpg_tag(sample, sample_tag)
        sample_blur = cv.blur(sample, ksize=(blur_size, blur_size))
        delta = cv.subtract(sample_blur, background_blur)
        delta = delta * dpg.get_value(brightness_slider_tag)
        # delta = ~delta
        to_dpg_tag(delta, delta_tag)

        keypoints = detector.detect(delta)
        if len(keypoints) == 1:
            success = True
            if not locations[led_index].initialized:
                locations[led_index].set(len(blobs), keypoints[0])
                blobs.append(keypoints[0])
            else:
                blob_index = locations[led_index].blob_index
                blobs[blob_index] = keypoints[0]
                locations[led_index].set(blob_index, keypoints[0])
        else:
            attempts += 1
            border_width = 10
            sample = cv.rectangle(
                sample,
                (0, 0),
                (sample.shape[1] - 1, sample.shape[0] - 1),
                (0, 0, 255),  # (B, G, R)
                border_width)
            to_dpg_tag(sample, sample_tag)
        im_with_keypoints = cv.drawKeypoints(sample, blobs, np.array([]), (0, 0, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        to_dpg_tag(im_with_keypoints, blobs_tag)
        return success


async def main():
    leds_init(display_brightness)
    leds_off()

    vid, test, texture_data = init_video()
    init_gui(vid, test, texture_data, switch_output, start_calibrate_thread, camera_brightness_multiplier, start_orchestrate_thread)

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    vid.release()
    dpg.destroy_context()
    leds_off()


asyncio.run(main())
