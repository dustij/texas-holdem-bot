"""
Window objects.
"""

__all__ = [
    'WindowElement',
    'WindowCapture'
]

__author__ = 'Dusti Johnson'
__copyright__ = '2023, Dusti Johnson'
__status__ = 'Development'

import time
from threading import Thread, Lock

import numpy as np
import win32con
import win32gui
import win32ui

from rectangle import Rectangle, Point


class WindowElement(Rectangle):
    """An element inside a window."""

    def __init__(self, window_rectangle: Rectangle, x: int, y: int, width: int, height: int,
                 name: str = None):
        super().__init__(x, y, width, height, name)
        self.window_rectangle = window_rectangle
        self.prev_frame = np.zeros([1, 1, 3])

    @property
    def global_top(self):
        return self._y + self.window_rectangle._y

    @property
    def global_bottom(self):
        return self._y + self._h + self.window_rectangle._y

    @property
    def global_left(self):
        return self._x + self.window_rectangle._x

    @property
    def global_right(self):
        return self._x + self._w + self.window_rectangle._x

    @property
    def global_top_left(self):
        return Point(self.global_left, self.global_top)

    @property
    def global_top_right(self):
        return Point(self.global_right, self.global_top)

    @property
    def global_bottom_left(self):
        return Point(self.global_left, self.global_bottom)

    @property
    def global_bottom_right(self):
        return Point(self.global_right, self.global_bottom)

    @property
    def center(self):
        return Point(self.global_left + self.width // 2, self.global_top + self.height // 2)

    def region(self, img):
        return img[self.top:self.bottom, self.left:self.right]

    def screenshot(self):
        hdesktop = win32gui.GetDesktopWindow()
        hwndDC = win32gui.GetWindowDC(hdesktop)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, self.width, self.height)

        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (self.width, self.height), mfcDC,
                      (self.global_left, self.global_top), win32con.SRCCOPY)

        bmpstr = saveBitMap.GetBitmapBits(True)

        img = np.fromstring(bmpstr, dtype='uint8')
        img.shape = (self.height, self.width, 4)
        img = img[..., :3]

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hdesktop, hwndDC)

        img = np.ascontiguousarray(img)
        return img


class WindowCapture:
    """Capture window."""

    # threading properties
    stopped = True
    lock = None
    screenshot = None

    # properties
    w = 0
    h = 0
    left = 0
    right = 0
    bottom = None
    hwnd = None
    win_size = (200, 200)

    def __init__(self, window_name=None):
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)

        # get the window size
        self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.hwnd)
        self.w = self.right - self.left
        self.h = self.bottom - self.top
        self.win_size = (self.w, self.h)

        # account for the window border and titlebar and cut them off
        border_pixels = 8
        titlebar_pixels = 31
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset, so we can translate
        # screenshot images_full into actual screen positions
        self.offset_right = self.right + self.cropped_x
        self.offset_botttom = self.bottom + self.cropped_y
        self.offset_left = self.left + self.cropped_x
        self.offset_top = self.top + self.cropped_y

        self.rect = Rectangle(self.offset_left, self.offset_top, self.w, self.h, "MainWindow")

    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))

        win32gui.EnumWindows(winEnumHandler, None)

    def get_screenshot(self):
        hdesktop = win32gui.GetDesktopWindow()
        hwndDC = win32gui.GetWindowDC(hdesktop)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, self.w, self.h)

        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (self.w, self.h), mfcDC, (self.offset_left, self.offset_top),
                      win32con.SRCCOPY)

        bmpstr = saveBitMap.GetBitmapBits(True)

        img = np.fromstring(bmpstr, dtype='uint8')
        img.shape = (self.h, self.w, 4)
        img = img[..., :3]

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hdesktop, hwndDC)

        img = np.ascontiguousarray(img)
        return img


if __name__ == '__main__':
    pass
