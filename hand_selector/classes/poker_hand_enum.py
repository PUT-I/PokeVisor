from enum import Enum


class PokerHand(Enum):
    unknown = "Unknown"
    highest_rank = "High Card"
    one_pair = "Pair"
    two_pairs = "Two pair"
    three_of_a_kind = "Three of a Kind"
    straight = "Straight"
    flush = "Flush"
    full_house = "Full House"
    four_of_a_kind = "Four of a Kind"
    royal_flush = "Royal Flush"

    def __str__(self):
        return self.value
