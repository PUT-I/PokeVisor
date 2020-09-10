from enums.card_suit_enum import CardSuit


class TrainSuits:
    """Structure to store information about train suit images."""

    def __init__(self):
        self.img = []  # Thresholded, sized suit image loaded from hard drive
        self.suit = CardSuit.unknown
