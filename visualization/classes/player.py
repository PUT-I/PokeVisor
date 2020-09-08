from typing import List, Dict

from card_detector.classes.poker_card import PokerCard
from chip_detector.classes.poker_chip_enum import PokerChip


class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.cards: List[PokerCard] = []
        self.chips: Dict[PokerChip, int] = {}

    def sum_chip_values(self):
        chip_sum = 0
        for chip in self.chips:
            chip_sum += chip.value * self.chips[chip]
        return chip_sum


def main():
    player = Player("Player 1")
    player.chips[PokerChip.purple] = 1
    player.chips[PokerChip.red] = 6
    player.chips[PokerChip.green] = 8

    print("Player {} has {} value in chips".format(player.name, player.sum_chip_values()))


if __name__ == "__main__":
    main()
