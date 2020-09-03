from card_detector.classes.card_rank_enum import CardRank


class TrainRanks:
    """Structure to store information about train rank images."""

    def __init__(self):
        self.img = []  # Thresholded, sized rank image loaded from hard drive
        self.rank = CardRank.unknown
