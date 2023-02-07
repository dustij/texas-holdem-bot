"""
Managers module.
"""

__all__ = [
    'WindowManager',
    'CaptureManager'
]

__author__ = 'Dusti Johnson'
__copyright__ = '2023, Dusti Johnson'
__status__ = 'Development'

import time

import cv2


class WindowManager:
    """A cv2 window to display the bot's vision."""

    def __init__(self, window_name, keypress_callback=None):
        self.keypress_callback = keypress_callback
        self.window_name = window_name
        self._is_window_created = False

    @property
    def is_window_created(self):
        return self._is_window_created

    def create_window(self):
        cv2.namedWindow(self.window_name)
        self._is_window_created = True

    def show(self, frame):
        cv2.imshow(self.window_name, frame)

    def destroy_window(self):
        cv2.destroyWindow(self.window_name)
        self._is_window_created = False

    def process_events(self):
        keycode = cv2.waitKey(1)
        if self.keypress_callback is not None and keycode != -1:
            self.keypress_callback(keycode)


class CaptureManager:
    def __init__(self, capture, preview_window_manager=None):
        self.preview_window_manager = preview_window_manager
        self._capture = capture
        self._entered_frame = False
        self._frame = None
        self._img = None
        self._image_filename = None
        self._start_time = None
        self._frames_elapsed = 0
        self.fps_estimate = None

    @property
    def frame(self):
        if self._entered_frame is not None and self._frame is None:
            self._frame = self._capture.get_screenshot()
        return self._frame

    @property
    def is_writing_image(self):
        return self._image_filename is not None

    def enter_frame(self):
        """Capture the next frame, if any."""
        # But first, check that any previous frame was exited.
        assert not self._entered_frame, 'previous enter_frame() had no matching exit_frame()'
        if self._capture is not None:
            self._entered_frame = self._capture.get_screenshot()

    def exit_frame(self):
        """Draw to the window. Write to files. Release the frame."""
        if self.frame is None:
            self._entered_frame = False
            return

        # Update the FPS estimate and related variables
        if self._frames_elapsed == 0:
            self._start_time = time.perf_counter()
        else:
            time_elapsed = time.perf_counter() - self._start_time
            self.fps_estimate = self._frames_elapsed / time_elapsed
            # print(f"\r{self._fps_estimate}", end="")
        self._frames_elapsed += 1

        # Draw to the window, if any
        if self.preview_window_manager is not None:
            self.preview_window_manager.show(self._frame)

        # Write to the image file, if any
        if self.is_writing_image:
            if self._img is not None:
                cv2.imwrite(self._image_filename, self._img)
            else:
                cv2.imwrite(self._image_filename, self._frame)

        # Release the frame
        self._frame = None
        self._entered_frame = False

    def write_image(self, filename, img=None):
        """Write frame or image to file."""
        if img is not None:
            self._img = img
        self._image_filename = filename


if __name__ == '__main__':
    pass
