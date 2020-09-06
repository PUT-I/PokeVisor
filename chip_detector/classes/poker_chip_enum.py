from enum import Enum


# Enumerate chip color types for use in classifier
class PokerChip(Enum):
    unknown = -1
    gray = 1
    red = 5
    blue = 10
    green = 25
    black = 100
    purple = 500
    yellow = 1000
