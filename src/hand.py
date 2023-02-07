"""
Poker hand object for comparing hands and returning hand strength.
"""

__all__ = []

__author__ = 'Dusti Johnson'
__copyright__ = '2023, Dusti Johnson'
__status__ = 'Development'

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

HAND_RANKS_CSV = Path(__file__).parent.joinpath('hand_ranks.csv').resolve()

SKLANSKY_CHUBUKOV = pd.read_csv(str(HAND_RANKS_CSV)).replace('inf', np.inf).set_index('Hand')


class Hand:
    """Poker hand representation."""

    def __init__(self, cards: List[str]):
        self.cards = self.parse_cards(cards)
        self.c1_rank = self.cards[0][0]
        self.c1_suit = self.cards[0][-1]
        self.c2_rank = self.cards[1][0]
        self.c2_suit = self.cards[1][-1]
        self.hand = self.parse_hand()

    def __eq__(self, other):
        return (
                SKLANSKY_CHUBUKOV.loc[self.hand, 'Ranking']
                == SKLANSKY_CHUBUKOV.loc[other.hand, 'Ranking']
        )

    def __lt__(self, other):
        return (
                SKLANSKY_CHUBUKOV.loc[self.hand, 'Ranking']
                > SKLANSKY_CHUBUKOV.loc[other.hand, 'Ranking']
        )

    def __gt__(self, other):
        return (
                SKLANSKY_CHUBUKOV.loc[self.hand, 'Ranking']
                < SKLANSKY_CHUBUKOV.loc[other.hand, 'Ranking']
        )

    def __repr__(self):
        return f"{self.hand} <{self.get_hand(verbose=True)}> | " \
               f"ranking= {SKLANSKY_CHUBUKOV.loc[self.hand, 'Ranking']} | " \
               f"percentile= {self.precentile * 100:.2f}"

    @property
    def precentile(self) -> float:
        return SKLANSKY_CHUBUKOV.loc[self.hand, 'Percentile']

    def get_hand(self, verbose: bool = False) -> str:
        if verbose:
            return ''.join(self.cards)
        else:
            return self.hand

    def in_range(self, percentile: float) -> bool:
        """Determine if hand is in top percentile range (0.0 - 1.0)"""
        return self.precentile >= percentile

    def parse_cards(self, cards: List[str]) -> List[str]:
        card_ranks_in_order = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        card_rank_1 = cards[0][0]
        card_rank_2 = cards[1][0]
        if card_ranks_in_order.index(card_rank_1) < card_ranks_in_order.index(card_rank_2):
            return cards
        else:
            return list(reversed(cards))

    def parse_hand(self) -> str:
        if self.c1_rank == self.c2_rank:
            return self.c1_rank + self.c2_rank
        elif self.c1_suit == self.c2_suit:
            return self.c1_rank + self.c2_rank + 's'
        else:
            return self.c1_rank + self.c2_rank + 'o'


if __name__ == '__main__':
    cards1 = ['As', 'Ts']
    cards2 = ['Ks', 'Ah']
    hand1 = Hand(cards1)
    hand2 = Hand(cards2)
    print(hand2)
    print(hand2.in_range(0.95))
    # print(SKLANSKY_CHUBUKOV)
