from enum import Enum


class PokerHand(Enum):
    highest_rank = 1
    one_pair = 2
    two_pairs = 3
    three_of_a_kind = 4
    straight = 5
    flush = 6
    full_house = 7
    four_of_a_kind = 8
    royal_flush = 9
