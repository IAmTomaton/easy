import math
import numpy as np
import win32con
import win32api
import time
import random
import win32gui
import win32ui
from PIL import Image
from easybot.bot import Bot


def take_screenshot():
    hwnd = win32gui.GetDesktopWindow()
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (x, y), win32con.SRCCOPY)

    bmp_info = saveBitMap.GetInfo()
    bmp_str = saveBitMap.GetBitmapBits(True)
    image = Image.frombuffer('RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'BGRX', 0, 1)

    return image


def random_sleep(delay):
    delay = (random.random() - 0.5) * 0.05 + delay
    time.sleep(delay)


def vector():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    random_sleep(0.95)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    random_sleep(0.35)


def get_red_pixels_from_rectangle(image, min_point, max_point):
    divider = 4
    for x in range(min_point[0], max_point[0] + 1):
        for y in range(min_point[1], max_point[1] + 1):
            pixel = image.getpixel((x * divider, y * divider))
            if pixel[0] > 250 and pixel[1] < 10 and pixel[2] < 10:
                yield np.array([x * divider, y * divider])


def get_closest_to_center_red_pixel(image):
    center = image.width / 2, image.height / 2
    first = True
    nearest_path = np.array([0, 0])
    for coord in get_red_pixels_from_rectangle(image, (-300, -250), (300, 150)):
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
    if num == 0:
        return 0
    return -1 if num < 0 else 1


class AimBot:

    def __init__(self):
        self._previous_direction = 0

    def aim(self):
        screen = take_screenshot()
        nearest_pixel = get_closest_to_center_red_pixel(screen)[0]
        direction = sign(nearest_pixel)
        print(nearest_pixel)

        velocity = 5 * direction # nearest_pixel / 3

        if direction != self._previous_direction:
            velocity /= 2

        self._previous_direction = direction

        win32api.mouse_event(win32con.MOUSE_MOVED, int_r(velocity), 0)

        time.sleep(0.01)


def main():
    bot = Bot(ord('L'))
    aim_bot = AimBot()
    bot.set_cyclical_macro(win32con.VK_XBUTTON1, vector)
    bot.set_cyclical_macro(ord('M'), aim_bot.aim)
    bot.start()


if __name__ == '__main__':
    main()
