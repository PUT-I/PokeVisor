from chip_detector.classes.chip_color_enum import ChipColor
from chip_detector.classes.chip_value_enum import ChipValue


class PokerChip:
    """Structure to store information about poker cards."""

    def __init__(self, color: ChipColor, value: ChipValue):
        self.color: ChipColor = color
        self.value: ChipValue = value

    def __repr__(self):
        return self.color.name + " " + self.value.name
