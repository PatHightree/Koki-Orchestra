import numpy as np
import dearpygui.dearpygui as dpg

window_tag = "window"
image_tag = "image"
background_tag = "background"
sample_tag = "sample"
delta_tag = "delta"
blobs_tag = "blobs"
start_tag = "start"
output_radio_tag = "output"
brightness_slider_tag = "brightness_multiplier"


def to_dpg(cv_frame):
    data = np.flip(cv_frame, 2)  # because the camera data comes in as BGR and we need RGB
    data = data.ravel()  # flatten camera data to a 1 d stricture
    data = np.asfarray(data, dtype='f')  # change data type to 32bit floats
    return np.true_divide(data, 255.0)  # normalize image data to prepare for GPU


def to_dpg_tag(cv_frame, tag):
    texture_data = to_dpg(cv_frame)
    dpg.set_value(tag, texture_data)


def init_gui(vid, test, texture_data, switch_output, start_calibrate_thread, capture_brightness_multiplier):
    dpg.create_context()
    dpg.create_viewport(title="Koki'orchestra", width=1920, height=1080)
    dpg.setup_dearpygui()
    # disabled theme doesn't work...
    with dpg.theme() as disabled_theme:
        with dpg.theme_component(dpg.mvInputFloat, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [255, 0, 0])
        with dpg.theme_component(dpg.mvInputInt, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [255, 0, 0])
    dpg.bind_theme(disabled_theme)

    with dpg.texture_registry(show=True):
        dpg.add_raw_texture(test.shape[1], test.shape[0], texture_data, format=dpg.mvFormat_Float_rgb, tag=background_tag, label=background_tag)
        dpg.add_raw_texture(test.shape[1], test.shape[0], texture_data, format=dpg.mvFormat_Float_rgb, tag=sample_tag, label=sample_tag)
        dpg.add_raw_texture(test.shape[1], test.shape[0], texture_data, format=dpg.mvFormat_Float_rgb, tag=delta_tag, label=delta_tag)
        dpg.add_raw_texture(test.shape[1], test.shape[0], texture_data, format=dpg.mvFormat_Float_rgb, tag=blobs_tag, label=blobs_tag)
    with dpg.window(tag=window_tag, label="Koki'orchestra", autosize=True):
        dpg.add_button(tag=start_tag, label="Start calibration", callback=start_calibrate_thread, user_data=vid)
        dpg.add_image(tag=image_tag, texture_tag=blobs_tag, show=True)
        dpg.add_radio_button(tag=output_radio_tag, items=[background_tag, delta_tag, blobs_tag], default_value=blobs_tag, callback=switch_output, horizontal=True, show=False)
        dpg.add_slider_int(tag=brightness_slider_tag, label="Capture brightness multiplier", min_value=1, max_value=10, default_value=capture_brightness_multiplier, show=False)
    dpg.show_metrics()
    dpg.show_viewport(maximized=True)

def switch_output(sender, data):
    dpg.configure_item(image_tag, texture_tag=dpg.get_value(output_radio_tag))


