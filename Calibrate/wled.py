import requests

url = 'http://192.168.122.149/json/state'


def leds_init(brightness):
    command = {"bri": brightness}
    requests.post(url, json=command)


def leds_off():
    a = [0, [0, 0, 0]]
    for l in range(1, 64):
        a.append(l)
        a.append([0, 0, 0])
    # command = {"seg":{"i":[0,[0,0,0],32,[0,0,0]]}}
    command = {"seg": {"i": a}}
    requests.post(url, json=command)


def leds_set(values):
    # values is a tuple of led_index and [r,g,b]
    a = []
    for index, val in enumerate(values):
        a.append(val[0])
        a.append(val[1])
    # command = {"seg":{"i":[0,[0,0,0],32,[0,0,0]]}}
    command = {"seg": {"i": a}}
    requests.post(url, json=command)


def led_set(i, val):
    command = {"seg": [{"i": [i, [val, val, val]]}]}
    requests.post(url, json=command)


def led_set_rgb(i, r, g, b):
    command = {"seg": [{"i": [i, [r, g, b]]}]}
    requests.post(url, json=command)
