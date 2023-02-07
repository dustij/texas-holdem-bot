"""
Use for development only.
"""

__all__ = []

__author__ = 'Dusti Johnson'
__copyright__ = '2023, Dusti Johnson'
__status__ = 'Development'

from functools import partial
from pathlib import Path

import cv2
import numpy as np

from conf import YamlConf
from managers import WindowManager, CaptureManager
from rectangle import Rectangle, Point
from window import WindowCapture

PROJECT_PATH = Path(__file__).parent.parent.resolve()

class Trackbars:
    """Trackbars window."""

    x = 456
    y = 410
    width = 62
    height = 4

    def __init__(self):
        cv2.namedWindow('Trackbars')
        cv2.createTrackbar('x', 'Trackbars', 456, 500, partial(self.set_attr, 'x'))
        cv2.createTrackbar('y', 'Trackbars', 410, 500, partial(self.set_attr, 'y'))
        cv2.createTrackbar('width', 'Trackbars', 62, 80, partial(self.set_attr, 'width'))
        cv2.createTrackbar('height', 'Trackbars', 4, 10, partial(self.set_attr, 'height'))

    def set_attr(self, name, value):
        self.__setattr__(name, int(value))


class Bot:
    """The Ignition Poker Hold'em bot."""

    def __init__(self):
        self.window_capture = WindowCapture(YamlConf.window_name)
        self.window_manager = WindowManager('TrackbarView', self.on_keypress)
        self.capture_manager = CaptureManager(self.window_capture, self.window_manager)
        self.trackbars = Trackbars()
        self.cropped_img = np.zeros((3, 3))

    def on_keypress(self, keycode):
        """Handle a keypress.
        escape -> Quit
        """
        if keycode == 27:  # escape
            self.window_manager.destroy_window()
        elif keycode == 32:  # space
            cv2.imwrite(str(PROJECT_PATH / 'temp' / 'trackbar_out.png'), self.cropped_img)
        elif keycode == 9:  # tab
            with open(PROJECT_PATH / 'temp' / 'trackbar.output', 'a') as f:
                f.write(f"Rectangle({self.trackbars.x}, {self.trackbars.y}, {self.trackbars.width}, {self.trackbars.height})\n")


    def run(self):
        """Run the main loop"""
        self.window_manager.create_window()
        while self.window_manager.is_window_created:
            self.capture_manager.enter_frame()
            frame = self.capture_manager.frame
            if np.any(frame):
                top_left = Point(self.trackbars.x, self.trackbars.y)
                bottom_right = Point(self.trackbars.x + self.trackbars.width,
                                self.trackbars.y + self.trackbars.height)
                r = Rectangle.from_points(top_left, bottom_right)
                self.cropped_img = r.cookie_cutter(frame)
                img = cv2.cvtColor(self.cropped_img, cv2.COLOR_BGR2GRAY)
                _, img = cv2.threshold(img, 190, 255, cv2.THRESH_BINARY)
                if np.count_nonzero(img) == 0:
                    print("\rNOT turn", end="")
                else:
                    print("\rplayers turn", end="")
                cv2.imshow('roi', self.cropped_img)
                # cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 1)
            self.capture_manager.exit_frame()
            self.window_manager.process_events()


if __name__ == '__main__':
    # print(ord(input()))
    Bot().run()
    # img = cv2.imread(str(PROJECT_PATH / 'temp' / 'trackbar_out.png'), cv2.IMREAD_UNCHANGED)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, img = cv2.threshold(img, 190, 255, cv2.THRESH_BINARY)
    # cv2.imwrite(str(PROJECT_PATH / 'temp' / 'threshold.png'), img)
