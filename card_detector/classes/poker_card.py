from card_detector.classes.card_rank_enum import CardRank
from card_detector.classes.card_suit_enum import CardSuit


class PokerCard:
    """Structure to store information about poker cards."""

    def __init__(self, rank: CardRank, suit: CardSuit):
        self.rank: CardRank = rank
        self.suit: CardSuit = suit

    def __repr__(self):
        return self.rank.name + " of " + self.suit.name

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        if self.suit.value < other.suit.value:
            return True
        if self.rank.value < other.rank.value:
            return True
        return False

    def is_unknown(self) -> bool:
        return self.rank == CardRank.unknown or self.suit == CardSuit.unknown
