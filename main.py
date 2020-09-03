import math
import numpy as np
import win32con
import win32api
import time
import random
import win32gui
import win32ui
from PIL import ImageGrab, Image
from easybot.bot import Bot


def random_sleep(delay):
    delay = (random.random() - 0.5) * 0.05 + delay
    time.sleep(delay)


def vector():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    random_sleep(0.65)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    random_sleep(0.45)


def crop_frame(image):
    image = image.crop()
    return image


def get_red_pixels(image):
    divider = 4
    for x in range(int(image.width / divider)):
        for y in range(int(image.height / divider)):
            pixel = image.getpixel((x * divider, y * divider))
            if pixel[0] > 250 and pixel[1] < 10 and pixel[2] < 10:
                yield np.array([x * divider, y * divider])


def get_nearest_pixel_by_image(image):
    center = image.width / 2, image.height / 2
    first = True
    nearest_path = np.array([0, 0])
    for coord in get_red_pixels(image):
        path = coord - center
        if first or vector_len(path) < vector_len(nearest_path):
            nearest_path = path
            first = False
    return nearest_path


def vector_len(v):
    return math.sqrt(np.dot(v, v))


def int_r(num):
    num = int(num + (0.5 if num > 0 else -0.5))
    return num


def sign(num):
    return -1 if num < 0 else 1


def get_nearest_pixel_to_cursor():
    height = 150
    width = 300
    t = time.time()
    frame = ImageGrab.grab(bbox=(1920 / 2 - width, 1080 / 2 - 100 - height, 1920 / 2 + width, 1080 / 2 + height))
#    print(time.time() - t)
    return get_nearest_pixel_by_image(frame)[0]


def get_divider(x):
    return


class AimBot:

    def __init__(self):
        self._previous_direction = 0

    def aim(self):
        nearest_pixel = get_nearest_pixel_to_cursor()
        direction = sign(nearest_pixel)

        velocity = nearest_pixel / 3

        if direction != self._previous_direction:
            velocity /= 2

        self._previous_direction = direction

        win32api.mouse_event(win32con.MOUSE_MOVED, int_r(velocity), 0)

        time.sleep(0.01)


def test_macro():
    print('PEW!')
    time.sleep(0.5)
    print('PEW!!')


def test_macro_move(distance):
    win32api.mouse_event(win32con.MOUSE_MOVED, int(distance), 0)


def solve(array):
    for i in range(2, len(array)):
        print(array[-i] / (array[-i] + array[-i - 1]))


def move_mouse(distance_x, distance_y):
    win32api.mouse_event(win32con.MOUSE_MOVED, distance_x, distance_y)
    time.sleep(0.1)


def test_screen():
    hwin = win32gui.GetDesktopWindow()
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)
    image = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)


def main():
    bot = Bot(ord('L'))
    aim_bot = AimBot()
    bot.set_cyclical_macro(win32con.VK_XBUTTON1, vector)
    bot.set_cyclical_macro(ord('M'), aim_bot.aim)
#    bot.set_cyclical_hold_macro(win32con.VK_DOWN, lambda: move_mouse(0, 20))
#    bot.set_cyclical_hold_macro(win32con.VK_UP, lambda: move_mouse(0, -20))
#    bot.set_cyclical_hold_macro(win32con.VK_LEFT, lambda: move_mouse(-80, 0))
#    bot.set_cyclical_hold_macro(win32con.VK_RIGHT, lambda: move_mouse(80, 0))
#    bot.set_single_macro(win32con.VK_XBUTTON1, lambda: test_macro_move(3142 / 5))
#    bot.set_single_macro(win32con.VK_XBUTTON2, lambda: test_macro_move(-20))
    bot.start()


if __name__ == '__main__':
    t = time.time()
    test_screen()
    print(time.time() - t)
