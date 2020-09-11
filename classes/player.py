from typing import List, Dict

from classes.poker_card import PokerCard
from enums.poker_chip_enum import PokerChip
from enums.poker_hand_enum import PokerHand


class Player:
    def __init__(self):
        self.cards: List[PokerCard] = []
        self.chips: Dict[PokerChip, int] = {}
        self.hand: PokerHand = PokerHand.unknown

    def add_chips(self, chips: List[PokerChip]):
        for chip in chips:
            self.add_chip(chip)

    def add_chip(self, chip: PokerChip):
        if chip in self.chips:
            self.chips[chip] += 1
        else:
            self.chips[chip] = 1

    def sum_chip_values(self):
        chip_sum = 0
        for chip in self.chips:
            chip_sum += chip.value * self.chips[chip]
        return chip_sum


def main():
    player = Player()
    player.chips[PokerChip.purple] = 1
    player.chips[PokerChip.red] = 6
    player.chips[PokerChip.green] = 8

    print("Player has {} value in chips".format(player.sum_chip_values()))


if __name__ == "__main__":
    main()
