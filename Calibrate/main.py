import asyncio
from wled import *
from video import *
from gui import *
from tags import *

camera_brightness_multiplier = 5
display_brightness = 100
led_value = 70
led_count = 64
blur_size = 10
delay = 100
blobs = []


async def main():
    leds_init(display_brightness)
    leds_off()

    vid, test, texture_data = init_video()
    init_gui(test, texture_data, switch_output, camera_brightness_multiplier)

    ret, background = vid.read()
    background_blur = cv.blur(background, ksize=(blur_size, blur_size))
    detector = cv.SimpleBlobDetector_create()
    led_index = -1
    while dpg.is_dearpygui_running():
        led_index = sample_led(background_blur, detector, led_index, vid)
        dpg.render_dearpygui_frame()

    vid.release()
    dpg.destroy_context()
    leds_off()


def sample_led(background_blur, detector, led_index, vid):
    led_set(led_index, 0)
    led_index = (led_index + 1) % led_count
    led_set(led_index, led_value)

    time.sleep(0.1)
    # await asyncio.sleep(0.1)

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
    return led_index


asyncio.run(main())
