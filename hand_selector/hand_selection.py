from itertools import combinations
from typing import List

from card_detector.classes.card_rank_enum import CardRank
from card_detector.classes.card_suit_enum import CardSuit
from card_detector.classes.poker_card import PokerCard
from hand_selector.classes.poker_hand_enum import PokerHand
from hand_selector.hand_checker import Checker


# exhaustive search using itertools.combinations
def play(hand: List[PokerCard], deck: List[PokerCard]):
    best_hand = PokerHand.highest_rank
    for i in range(6):
        possible_combos = combinations(hand, 5 - i)
        for combo in possible_combos:
            current_hand = list(combo) + deck[:i]
            current_hand = Checker.check_hand(current_hand)
            if current_hand.value > best_hand.value:
                best_hand = current_hand

    return best_hand


def main():
    hand = [PokerCard(CardRank.ace, CardSuit.hearts), PokerCard(CardRank.five, CardSuit.hearts),
            PokerCard(CardRank.two, CardSuit.hearts), PokerCard(CardRank.three, CardSuit.hearts),
            PokerCard(CardRank.four, CardSuit.hearts)]
    deck = [PokerCard(CardRank.five, CardSuit.spades), PokerCard(CardRank.six, CardSuit.diamonds)]
    print(play(hand, deck))


if __name__ == "__main__":
    main()
