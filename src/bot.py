import glob
import time
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Callable, Type

import cv2
import imagehash
import numpy as np
from loguru import logger
from PIL import Image

from conf import YamlConf
from managers import WindowManager, CaptureManager
from window import WindowCapture, WindowElement
from events import HandEvents, HandListener, HandState, BoardEvents, BoardListener, BoardState

PROJECT_PATH = Path(__file__).parent.parent.resolve()
SRC_PATH = PROJECT_PATH / 'src'
IMAGES_PATH = SRC_PATH / 'images'
CARD_IMAGES_PATH = IMAGES_PATH / 'cards'


class BotOutput:
    fps = 0
    hand_state = HandState.SITTING_OUT
    hole_cards = []
    board_state = BoardState.PREFLOP
    community_cards = []

    def print(self):
        UP = "\x1B[7A"
        CLR = "\x1B[0K"
        HIDE_CURSOR = '\033[?25l'

        left_width = 20
        right_width = 35

        print(
            f"{HIDE_CURSOR}",
            f"{UP}" + f" Texas Hold'em Bot ".center(left_width + right_width, '-'),
            f"{CLR}\n",
            f"FPS".ljust(left_width, '.')
            + f"{self.fps}".rjust(right_width),
            f"{CLR}\n",
            f"Hand state".ljust(left_width, '.')
            + f"{self.hand_state}".rjust(right_width),
            f"{CLR}\n",
            f"Hole cards".ljust(left_width, '.')
            + f"{self.hole_cards}".rjust(right_width),
            f"{CLR}\n",
            f"Board state".ljust(left_width, '.')
            + f"{self.board_state}".rjust(right_width),
            f"{CLR}\n",
            f"Community cards".ljust(left_width, '.')
            + f"{self.community_cards}".rjust(right_width),
            f"{CLR}\n",
        )


class Bot:
    """The Ignition Poker Hold'em bot."""

    def __init__(self):
        # self.window_capture = WindowCapture()
        self.window_capture = WindowCapture(YamlConf.window_name)
        self.window_manager = WindowManager('PokerBot', self.on_keypress)
        self.capture_manager = CaptureManager(self.window_capture, self.window_manager)
        self.poll_times = defaultdict(dict)
        self.animation_frames = {}
        self.currently_animating = {}
        self.window_elements = {
            'board': Type[WindowElement],
            'c_cards': [],
            'c_check_pixels': [],
            'h_cards': [],
            'h_check_pixel': Type[WindowElement],
        }
        self.card_images = []
        self.card_names = []
        self.load_card_images()
        self.hashed_cards = {}
        self.hash_card_images()
        self.c_cards = []
        self.h_cards = []
        self.init_elements()
        self.hand_events = HandEvents()
        self.hand_listener = HandListener(self)
        self.hand_events.add(self.hand_listener)
        self.board_events = BoardEvents()
        self.board_listener = BoardListener(self)
        self.board_events.add(self.board_listener)
        self.output = BotOutput()

    def init_elements(self):
        # Hole cards
        x = 442
        y = 328
        self.window_elements['h_cards'].append(
            WindowElement(self.window_capture.rect, x, y, 35, 42))
        x = 480
        self.window_elements['h_cards'].append(
            WindowElement(self.window_capture.rect, x, y, 35, 42))

        # Hand
        x = self.window_elements['h_cards'][0].left
        y = self.window_elements['h_cards'][0].top
        w = self.window_elements['h_cards'][-1].right - x
        h = self.window_elements['h_cards'][-1].bottom - y
        self.window_elements['hand'] = WindowElement(self.window_capture.rect, x, y, w, h)

        # Hole check pixel
        self.window_elements['h_check_pixel'] = WindowElement(
            self.window_capture.rect, 470, 330, 1, 1)

        # Community cards
        x = 335
        y = 211
        self.window_elements['c_cards'].append(
            WindowElement(self.window_capture.rect, x, y, 49, 59))
        x = 395
        self.window_elements['c_cards'].append(
            WindowElement(self.window_capture.rect, x, y, 49, 59))
        x = 455
        self.window_elements['c_cards'].append(
            WindowElement(self.window_capture.rect, x, y, 49, 59))
        x = 514
        self.window_elements['c_cards'].append(
            WindowElement(self.window_capture.rect, x, y, 49, 59))
        x = 574
        self.window_elements['c_cards'].append(
            WindowElement(self.window_capture.rect, x, y, 49, 59))

        # Board
        x = self.window_elements['c_cards'][0].left
        y = self.window_elements['c_cards'][0].top
        w = self.window_elements['c_cards'][-1].right - x
        h = self.window_elements['c_cards'][-1].bottom - y
        self.window_elements['board'] = WindowElement(self.window_capture.rect, x, y, w, h)

        # Community check pixels
        self.window_elements['c_check_pixels'].append(
            WindowElement(self.window_capture.rect, 496, 220, 1, 1))
        self.window_elements['c_check_pixels'].append(
            WindowElement(self.window_capture.rect, 556, 220, 1, 1))
        self.window_elements['c_check_pixels'].append(
            WindowElement(self.window_capture.rect, 612, 220, 1, 1))

    def load_card_images(self):
        files = Path(CARD_IMAGES_PATH).glob('*')
        for file in files:
            img = cv2.imread(str(file), cv2.IMREAD_UNCHANGED)
            name = str(file)[-6:-4]
            self.card_names.append(name)
            self.card_images.append(img)

    def hash_card_images(self):
        files = Path(CARD_IMAGES_PATH).glob('*')
        for file in files:
            name = str(file)[-6:-4]
            hash = imagehash.phash(Image.open(file))
            self.hashed_cards[hash] = name

    def on_keypress(self, keycode):
        """Handle a keypress.
        escape -> Quit
        """
        if keycode == 27:  # escape
            self.window_manager.destroy_window()

    def poll(self, func: Callable, frame: np.ndarray, name: str, duration: float):
        if not self.poll_times[func.__name__]:
            self.poll_times[func.__name__]['start'] = {name: False}
            self.poll_times[func.__name__]['duration'] = {name: 0}

        if not self.poll_times[func.__name__]['start'].get(name, False):
            self.poll_times[func.__name__]['start'][name] = time.time()
        self.poll_times[func.__name__]['duration'][name] = duration
        func(frame, name)

    def poll_animation(self, frame, name):
        start = self.poll_times['poll_animation']['start'][name]
        duration = self.poll_times['poll_animation']['duration'][name]
        current_frame = self.window_elements[name].region(frame)
        prev_frame = self.animation_frames.get(name, self.window_elements[name].region(frame))
        if time.time() - start < duration:
            if not np.array_equiv(prev_frame, current_frame):
                self.animation_frames[name] = current_frame
                self.currently_animating[name] = True
        else:
            self.poll_times['poll_animation']['start'][name] = False
            self.animation_frames[name] = current_frame
            self.currently_animating[name] = False

    @logger.catch
    def run(self):
        """Run the main loop"""
        self.window_manager.create_window()
        while self.window_manager.is_window_created:
            self.capture_manager.enter_frame()
            frame = self.capture_manager.frame
            if np.any(frame):
                self.poll(self.poll_animation, frame, 'hand', 1)
                self.check_hand_events()
                self.poll(self.poll_animation, frame, 'board', 1)
                self.check_board_events()
                self.update_output()
                # cv2.imshow('test', self.window_elements['board'].region(frame))
                # cv2.waitKey(-1)
            self.capture_manager.exit_frame()
            self.window_manager.process_events()

    def check_board_events(self):
        river_card_px: WindowElement = self.window_elements['c_check_pixels'][2]
        turn_card_px: WindowElement = self.window_elements['c_check_pixels'][1]
        flop_card_px: WindowElement = self.window_elements['c_check_pixels'][0]
        # Wait for animation to stop
        if not self.currently_animating.get('board', False):
            if np.mean(river_card_px.screenshot()) == 255:
                self.board_events.river()
            elif np.mean(turn_card_px.screenshot()) == 255:
                self.board_events.turn()
            elif np.mean(flop_card_px.screenshot()) == 255:
                self.board_events.flop()
            else:
                self.board_events.preflop()

    def check_hand_events(self):
        hole_card_px: WindowElement = self.window_elements['h_check_pixel']
        # Wait for animation to stop
        if not self.currently_animating.get('hand', False):
            if np.mean(hole_card_px.screenshot()) == 255:
                self.hand_events.playing()
            else:
                self.hand_events.sitting_out()

    def update_output(self):
        self.output.fps = self.capture_manager.fps_estimate
        self.output.hand_state = self.hand_events.current_state
        self.output.hole_cards = self.h_cards
        self.output.board_state = self.board_events.current_state
        self.output.community_cards = self.c_cards
        self.output.print()
