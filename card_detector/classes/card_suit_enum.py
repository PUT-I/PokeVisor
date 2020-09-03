from enum import Enum


# Enumerate chip color types for use in classifier
class CardSuit(Enum):
    unknown = -1
    clubs = 0
    diamonds = 1
    hearts = 2
    spades = 3
