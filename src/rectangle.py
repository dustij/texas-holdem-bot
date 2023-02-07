"""
A rectangle.
"""

__all__ = []

__author__ = 'Dusti Johnson'
__copyright__ = '2023, Dusti Johnson'

from typing import NamedTuple

import numpy as np
import win32con
import win32gui
import win32ui


class Point(NamedTuple):
    """(x, y) coordinate"""
    x: int
    y: int


class Rectangle:
    """A rectangle object."""

    def __init__(self, x: int, y: int, width: int, height: int, name: str = None):
        self.name = name
        self._parent = None
        self._x = x
        self._y = y
        self._w = width
        self._h = height

    def __repr__(self):
        return f"Rectangle(name={self.name}, x={self.left}, y={self.top}, width={self.width}, height={self.height})"

    def __iter__(self):
        keys = ('x', 'y', 'width', 'height')
        values = (self.left, self.top, self.width, self.height)
        for k, v in zip(keys, values):
            yield (k, v)

    @classmethod
    def from_points(cls, top_left: Point, bottom_right: Point) -> 'Rectangle':
        """Creates a new :class:`Rectangle` object from two points.

        :param top_left: Top left corner
        :type top_left: :class:`Point`
        :param bottom_right: Bottom right corner
        :type bottom_right: :class:`Point`
        :return: :class:`Rectangle`
        """
        return cls(
            top_left.x,
            top_left.y,
            bottom_right.x - top_left.x,
            bottom_right.y - top_left.y,
        )

    @property
    def top(self):
        return self._y

    @top.setter
    def top(self, value):
        self._y = value

    @property
    def bottom(self):
        return self._y + self._h

    @bottom.setter
    def bottom(self, value):
        self._h = value - self._y

    @property
    def left(self):
        return self._x

    @left.setter
    def left(self, value):
        self._x = value

    @property
    def right(self):
        return self._x + self._w

    @right.setter
    def right(self, value):
        self._w = value - self._x

    @property
    def width(self):
        return self._w

    @width.setter
    def width(self, value):
        self._w = value

    @property
    def height(self):
        return self._h

    @height.setter
    def height(self, value):
        self._h = value

    @property
    def top_left(self):
        return Point(self.left, self.top)

    @property
    def top_right(self):
        return Point(self.right, self.top)

    @property
    def bottom_left(self):
        return Point(self.left, self.bottom)

    @property
    def bottom_right(self):
        return Point(self.right, self.bottom)

    @property
    def center(self):
        return Point(self.left + self.width // 2, self.top + self.height // 2)

    @property
    def parent(self) -> 'Rectangle':
        return self._parent

    @parent.setter
    def parent(self, value: 'Rectangle'):
        inside_left = value.left <= self.left
        inside_right = value.right >= self.right
        inside_top = value.top <= self.top
        inside_bottom = value.bottom >= self.bottom

        if not inside_left or not inside_right or not inside_top or not inside_bottom:
            raise ValueError(
                "%s must be inside %s.parent. One or more of the sides falls outside of parent "
                "dimensions\ninside left = %s\ninside right = %s\ninside top = %s"
                "\ninside bottom = %s" %
                (
                    self.__class__.__name__, self.__class__.__name__,
                    inside_left, inside_right, inside_top, inside_bottom
                )
            )

        self._parent = value

    def cookie_cutter(self, img: np.ndarray):
        return img[self.top:self.bottom, self.left:self.right]

    def screenshot(self):
        hdesktop = win32gui.GetDesktopWindow()
        hwndDC = win32gui.GetWindowDC(hdesktop)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, self.width, self.height)

        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (self.width, self.height), mfcDC, (self.left, self.top),
                      win32con.SRCCOPY)

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


if __name__ == '__main__':
    pass
