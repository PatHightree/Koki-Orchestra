import requests

# url = 'http://192.168.122.149/json/state'
url = 'http://192.168.122.185/json/state'
led_count = 64

def rgb_to_hex(r, g, b):
    return "{0:02x}{1:02x}{2:02x}".format(r, g, b)


def rgb_to_hex_list(values):
    return "{0:02x}{1:02x}{2:02x}".format(values[0], values[1], values[2])


def leds_init(brightness):
    command = {"bri": brightness}
    requests.post(url, json=command)


def leds_off():
    command = {"seg": {"i": [0, led_count, [0, 0, 0]]}}
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


def leds_set_rle(values):
    # values is a tuple of led_index and [r,g,b]
    a = []
    i = 0
    while i < len(values):
        count = 1
        j = i
        while j < len(values)-1:
            if values[j][1] == values[j+1][1]:
                count += 1
                j += 1
            else:
                break
        if count == 1:
            a.append(i)
            a.append(values[i][1])
        else:
            a.append(i)
            a.append(j+1)
            a.append(values[i][1])
        i = j+1
    # command = {"seg":{"i":[0,32,[0,0,0],32,64,[0,0,0]]}}  # end of range is inclusive!
    command = {"seg": {"i": a}}
    requests.post(url, json=command)


def led_set(i, val):
    command = {"seg": [{"i": [i, [val, val, val]]}]}
    requests.post(url, json=command)


def led_set_rgb(i, r, g, b):
    command = {"seg": [{"i": [i, [r, g, b]]}]}
    requests.post(url, json=command)
