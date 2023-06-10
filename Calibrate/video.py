import cv2 as cv
import time
from gui import to_dpg


def init_video():
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
    return vid, test, texture_data


def list_ports():
    """
    Test the ports and returns a tuple with the available ports
    and the ones that are working.
    """
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
            print("Port %s is not working." % dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" % (dev_port, h, w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." % (dev_port, h, w))
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports

