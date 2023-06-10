import numpy as np
import dearpygui.dearpygui as dpg
from tags import *


def to_dpg(cv_frame):
    data = np.flip(cv_frame, 2)  # because the camera data comes in as BGR and we need RGB
    data = data.ravel()  # flatten camera data to a 1 d stricture
    data = np.asfarray(data, dtype='f')  # change data type to 32bit floats
    return np.true_divide(data, 255.0)  # normalize image data to prepare for GPU


def to_dpg_tag(cv_frame, tag):
    texture_data = to_dpg(cv_frame)
    dpg.set_value(tag, texture_data)


def init_gui(test, texture_data, switch_output, capture_brightness_multiplier):
    dpg.create_context()
    dpg.create_viewport(title='Custom Title', width=1920, height=1080)
    dpg.setup_dearpygui()
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
        dpg.add_radio_button(tag=output_tag, items=[blobs_tag, background_tag, delta_tag], default_value=blobs_tag,
                             callback=switch_output, horizontal=True)
        dpg.add_image(tag=image_tag, texture_tag=blobs_tag, show=True)
    dpg.set_value("capture_brightness_multiplier", capture_brightness_multiplier)
    dpg.show_metrics()
    dpg.show_viewport(maximized=True)


def switch_output(sender, data):
    dpg.configure_item(image_tag, texture_tag=dpg.get_value(output_tag))


