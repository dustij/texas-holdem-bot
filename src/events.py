"""
# TODO document this module
"""

__all__ = []

__author__ = 'Dusti Johnson'
__copyright__ = '2023, Dusti Johnson'
__status__ = 'Development'

from abc import ABC, abstractmethod
from enum import Enum

import cv2
import imagehash
import numpy as np
from PIL import Image
from loguru import logger

from hand import Hand


class Listener(ABC):
    @abstractmethod
    def notify(self, event):
        pass


class Event:
    listeners = []

    def add(self, listener: 'Listener'):
        if listener not in self.listeners:
            self.listeners.append(listener)
        else:
            logger.warning(
                f"{self.__class__.__name__} failed to add {listener.__class__.__name__}")

    def remove(self, listener: 'Listener'):
        try:
            self.listeners.remove(listener)
        except ValueError:
            logger.warning(
                f"{self.__class__.__name__} failed to remove {listener.__class__.__name__}")

    def notify(self):
        [listener.notify(self) for listener in self.listeners]


class BoardState(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3


class BoardEvents(Event):
    current_state = BoardState.PREFLOP

    def preflop(self):
        if self.current_state != BoardState.PREFLOP:
            self.current_state = BoardState.PREFLOP
            self.notify()

    def flop(self):
        if self.current_state != BoardState.FLOP:
            self.current_state = BoardState.FLOP
            self.notify()

    def turn(self):
        if self.current_state != BoardState.TURN:
            self.current_state = BoardState.TURN
            self.notify()

    def river(self):
        if self.current_state != BoardState.RIVER:
            self.current_state = BoardState.RIVER
            self.notify()


class BoardListener(Listener):
    def __init__(self, bot):
        self.bot = bot

    def notify(self, event: 'BoardEvents'):
        if event.current_state == BoardState.PREFLOP:
            self.bot.c_cards = []
        elif event.current_state == BoardState.FLOP:
            c0_rect = self.bot.window_elements['c_cards'][0]
            c1_rect = self.bot.window_elements['c_cards'][1]
            c2_rect = self.bot.window_elements['c_cards'][2]
            c0_img = cv2.resize(c0_rect.screenshot(), (35, 42))
            c1_img = cv2.resize(c1_rect.screenshot(), (35, 42))
            c2_img = cv2.resize(c2_rect.screenshot(), (35, 42))
            try:
                self.bot.c_cards.append(self.bot.hashed_cards[self.get_hash(c0_img)])
            except KeyError:
                self.bot.c_cards.append(self.get_best_match(c0_img))
            try:
                self.bot.c_cards.append(self.bot.hashed_cards[self.get_hash(c1_img)])
            except KeyError:
                self.bot.c_cards.append(self.get_best_match(c1_img))
            try:
                self.bot.c_cards.append(self.bot.hashed_cards[self.get_hash(c2_img)])
            except KeyError:
                self.bot.c_cards.append(self.get_best_match(c2_img))
        elif event.current_state == BoardState.TURN:
            c3_rect = self.bot.window_elements['c_cards'][3]
            c3_img = cv2.resize(c3_rect.screenshot(), (35, 42))
            try:
                self.bot.c_cards.append(self.bot.hashed_cards[self.get_hash(c3_img)])
            except KeyError:
                self.bot.c_cards.append(self.get_best_match(c3_img))
        elif event.current_state == BoardState.RIVER:
            c4_rect = self.bot.window_elements['c_cards'][4]
            c4_img = cv2.resize(c4_rect.screenshot(), (35, 42))
            if len(self.bot.c_cards) >= 5:
                return
            try:
                self.bot.c_cards.append(self.bot.hashed_cards[self.get_hash(c4_img)])
            except KeyError:
                self.bot.c_cards.append(self.get_best_match(c4_img))

    def get_hash(self, img: np.ndarray):
        img = Image.fromarray(img)
        return imagehash.phash(img)

    def get_best_match(self, img):
        best_match = ""
        best_rank = 1000
        for card_img, card_name in zip(self.bot.card_images, self.bot.card_names):
            dif = cv2.absdiff(card_img, img)
            rank = int(np.sum(dif) / 255)
            if rank < best_rank:
                best_rank = rank
                best_match = card_name
        return best_match


class HandState(Enum):
    PLAYING = 0
    SITTING_OUT = 1


class HandEvents(Event):
    current_state = HandState.SITTING_OUT

    def playing(self):
        if self.current_state != HandState.PLAYING:
            self.current_state = HandState.PLAYING
            self.notify()

    def sitting_out(self):
        if self.current_state != HandState.SITTING_OUT:
            self.current_state = HandState.SITTING_OUT
            self.notify()


class HandListener(Listener):
    def __init__(self, bot):
        self.bot = bot

    def notify(self, event: 'HandEvents'):
        if event.current_state == HandState.SITTING_OUT:
            self.bot.h_cards = []
            self.bot.hand = None
        elif event.current_state == HandState.PLAYING:
            c0_rect = self.bot.window_elements['h_cards'][0]
            c1_rect = self.bot.window_elements['h_cards'][1]
            c0_img = cv2.resize(c0_rect.screenshot(), (35, 42))
            c1_img = cv2.resize(c1_rect.screenshot(), (35, 42))
            try:
                self.bot.h_cards.append(self.bot.hashed_cards[self.get_hash(c0_img)])
            except KeyError:
                self.bot.h_cards.append(self.get_best_match(c0_img))
            try:
                self.bot.h_cards.append(self.bot.hashed_cards[self.get_hash(c1_img)])
            except KeyError:
                self.bot.h_cards.append(self.get_best_match(c1_img))
            self.bot.hand = Hand(self.bot.h_cards)

    def get_hash(self, img: np.ndarray):
        img = Image.fromarray(img)
        return imagehash.phash(img)

    def get_best_match(self, img):
        best_match = ""
        best_rank = 1000
        for card_img, card_name in zip(self.bot.card_images, self.bot.card_names):
            dif = cv2.absdiff(card_img, img)
            rank = int(np.sum(dif) / 255)
            if rank < best_rank:
                best_rank = rank
                best_match = card_name
        return best_match


if __name__ == '__main__':
    pass
