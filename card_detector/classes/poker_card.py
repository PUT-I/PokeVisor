from card_detector.classes.card_rank_enum import CardRank
from card_detector.classes.card_suit_enum import CardSuit


class PokerCard:
    """Structure to store information about poker cards."""

    def __init__(self, rank: CardRank, suit: CardSuit):
        self.rank: CardRank = rank
        self.suit: CardSuit = suit

    def __repr__(self):
        return self.rank.name + " of " + self.suit.name

    def is_unknown(self) -> bool:
        return self.rank == CardRank.unknown or self.suit == CardSuit.unknown
