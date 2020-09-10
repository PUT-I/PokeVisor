from enum import Enum


class PokerHand(Enum):
    unknown = "0 Unknown"
    high_card = "1 High Card"
    pair = "2 Pair"
    two_pairs = "3 Two pair"
    three_of_a_kind = "4 Three of a Kind"
    straight = "5 Straight"
    flush = "6 Flush"
    full_house = "7 Full House"
    four_of_a_kind = "8 Four of a Kind"
    royal_straight = "9 Royal Straight"
    royal_flush = "10 Royal Flush"

    def __str__(self):
        return self.value[2:]
