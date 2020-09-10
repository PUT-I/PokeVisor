from enum import Enum


# Enumerate chip color types for use in classifier
class CardSuit(Enum):
    unknown = 0
    clubs = 1
    diamonds = 2
    hearts = 3
    spades = 4
