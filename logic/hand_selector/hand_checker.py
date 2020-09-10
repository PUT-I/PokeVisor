from collections import defaultdict
from itertools import combinations
from typing import List

from classes.poker_card import PokerCard
from enums.card_rank_enum import CardRank
from enums.card_suit_enum import CardSuit
# hand is best 5 cards
from enums.poker_hand_enum import PokerHand


class Checker:

    @staticmethod
    def get_best_hand(player_cards: List[PokerCard], community_cards: List[PokerCard]) -> PokerHand:
        best_hand = PokerHand.highest_rank
        for i in range(6):
            possible_combos = combinations(player_cards, 5 - i)
            for combo in possible_combos:
                current_hand = list(combo) + community_cards[:i]
                current_hand = Checker.check_hand(current_hand)
                if current_hand.value > best_hand.value:
                    best_hand = current_hand

        return best_hand

    @staticmethod
    def check_hand(hand: List[PokerCard]) -> PokerHand:
        if Checker._check_royal_flush(hand):
            return PokerHand.royal_flush
        if Checker._check_four_of_a_kind(hand):
            return PokerHand.four_of_a_kind
        if Checker._check_full_house(hand):
            return PokerHand.full_house
        if Checker._check_flush(hand):
            return PokerHand.flush
        if Checker._check_straight(hand):
            return PokerHand.straight
        if Checker._check_three_of_a_kind(hand):
            return PokerHand.three_of_a_kind
        if Checker._check_two_pair(hand):
            return PokerHand.two_pairs
        if Checker._check_pair(hand):
            return PokerHand.one_pair
        return PokerHand.highest_rank

    @staticmethod
    def _check_royal_flush(hand: List[PokerCard]) -> bool:
        if Checker._check_flush(hand) and Checker._check_straight(hand):
            return True
        else:
            return False

    @staticmethod
    def _check_four_of_a_kind(hand: List[PokerCard]) -> bool:
        ranks = [card.rank.value for card in hand]
        for rank in set(ranks):
            if ranks.count(rank) == 4:
                return True
        return False

    @staticmethod
    def _check_full_house(hand: List[PokerCard]) -> bool:
        ranks = [card.rank.value for card in hand]
        rank_count = defaultdict(int)
        for rank in ranks:
            rank_count[rank] += 1
        if sorted(rank_count.values()) == [2, 3]:
            return True
        else:
            return False

    @staticmethod
    def _check_flush(hand: List[PokerCard]) -> bool:
        suits = [card.suit.value for card in hand]
        if len(set(suits)) == 1:
            return True
        else:
            return False

    @staticmethod
    def _check_straight(hand: List[PokerCard]) -> bool:
        ranks = [card.rank.value for card in hand]
        ranks = sorted(ranks)

        specific_straight = [CardRank.ace, CardRank.ten, CardRank.jack, CardRank.queen, CardRank.king]
        if ranks == [rank.value for rank in specific_straight]:
            return True

        for i in range(0, len(ranks) - 1):
            if ranks[i] != ranks[i + 1] - 1:
                return False
        return True

    @staticmethod
    def _check_three_of_a_kind(hand: List[PokerCard]) -> bool:
        ranks = [card.rank.value for card in hand]
        for rank in set(ranks):
            if ranks.count(rank) == 3:
                return True
        return False

    @staticmethod
    def _check_two_pair(hand: List[PokerCard]) -> bool:
        ranks = [card.rank.value for card in hand]
        rank_count = defaultdict(int)
        for rank in ranks:
            rank_count[rank] += 1
        if sorted(rank_count.values()) == [1, 2, 2]:
            return True
        else:
            return False

    @staticmethod
    def _check_pair(hand: List[PokerCard]) -> bool:
        ranks = [card.rank.value for card in hand]
        if len(set(ranks)) == len(hand) - 1:
            return True
        else:
            return False


def get_best_hand_example():
    hand = [PokerCard(CardRank.ace, CardSuit.hearts), PokerCard(CardRank.five, CardSuit.hearts),
            PokerCard(CardRank.two, CardSuit.hearts), PokerCard(CardRank.three, CardSuit.hearts),
            PokerCard(CardRank.four, CardSuit.hearts)]
    deck = [PokerCard(CardRank.five, CardSuit.spades), PokerCard(CardRank.six, CardSuit.diamonds)]
    print(Checker.get_best_hand(hand, deck))


def check_hand_examples():
    card_1 = PokerCard(CardRank.ace, CardSuit.hearts)
    card_2 = PokerCard(CardRank.king, CardSuit.spades)
    card_3 = PokerCard(CardRank.nine, CardSuit.spades)

    hand_1 = [card_2, card_2]
    hand_2 = [card_1, card_1, card_2, card_2, card_3]
    hand_3 = [card_1, card_1, card_1, card_2, card_3]
    hand_4 = [card_1, PokerCard(CardRank.five, CardSuit.spades), PokerCard(CardRank.two, CardSuit.hearts),
              PokerCard(CardRank.three, CardSuit.hearts), PokerCard(CardRank.four, CardSuit.hearts)]
    hand_5 = [card_1, PokerCard(CardRank.ten, CardSuit.spades), PokerCard(CardRank.queen, CardSuit.hearts),
              PokerCard(CardRank.jack, CardSuit.hearts), PokerCard(CardRank.king, CardSuit.hearts)]
    hand_6 = [card_1, card_1, card_1, card_2, card_2]
    hand_7 = [card_1, card_1, card_1, card_1, card_3]

    print("Is {} pair: {}".format(hand_1, Checker._check_pair(hand_1)))
    print("Is {} two pair: {}".format(hand_2, Checker._check_two_pair(hand_2)))
    print("Is {} three of a king: {}".format(hand_3, Checker._check_three_of_a_kind(hand_3)))
    print("Is {} straight: {}".format(hand_4, Checker._check_straight(hand_4)))
    print("Is {} straight: {}".format(hand_5, Checker._check_straight(hand_5)))
    print("Is {} full house: {}".format(hand_6, Checker._check_full_house(hand_6)))
    print("Is {} four of a kind: {}".format(hand_7, Checker._check_four_of_a_kind(hand_7)))
    print("Is {} four of a kind: {}".format(hand_3, Checker._check_four_of_a_kind(hand_3)))
    print("Is {} royal flush: {}".format(hand_4, Checker._check_four_of_a_kind(hand_4)))


def main():
    get_best_hand_example()
    check_hand_examples()


if __name__ == "__main__":
    main()
