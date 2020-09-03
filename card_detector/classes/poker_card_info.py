from card_detector.classes.card_rank_enum import CardRank
from card_detector.classes.card_suit_enum import CardSuit
from card_detector.classes.poker_card import PokerCard


class PokerCardInfo:
    """Structure to store information about poker cards in the camera image."""

    def __init__(self):
        self.contour = []  # Contour of card
        self.width, self.height = 0, 0  # Width and height of card
        self.center = []  # Center point of card
        self.rank_img = []  # Thresholded, sized image of card's rank
        self.suit_img = []  # Thresholded, sized image of card's suit
        self.best_rank_match: CardRank = CardRank.unknown  # Best matched rank
        self.best_suit_match: CardSuit = CardSuit.unknown  # Best matched suit
        self.rank_diff = 0  # Difference between rank image and best matched train rank image
        self.suit_diff = 0  # Difference between suit image and best matched train suit image

    def __repr__(self):
        return self.best_rank_match + ' of ' + self.best_suit_match

    def to_poker_card(self) -> PokerCard:
        return PokerCard(self.best_rank_match, self.best_suit_match)
