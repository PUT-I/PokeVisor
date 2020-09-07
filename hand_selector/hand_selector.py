from itertools import combinations
from poker_card import PokerCard
from hand_checker import Checker

hand_dict = {9:"royal-flush", 8:"four-of-a-kind", 7:"full-house", 6:"flush", 5:"straight", 4:"three-of-a-kind", 3:"two-pairs", 2:"one-pair", 1:"highest-card"}

#exhaustive search using itertools.combinations
def play(cards):
    hand = cards[:5]
    deck = cards[5:]
    best_hand = 0
    for i in range(6):
        possible_combos = combinations(hand, 5-i)
        for c in possible_combos: 
            current_hand = list(c) + deck[:i]
            hand_value = Checker.check_hand(current_hand)
            if hand_value > best_hand:
                best_hand = hand_value
                
    return hand_dict[best_hand]


print(play([PokerCard(1,3),PokerCard(5,3),PokerCard(2,3),PokerCard(3,3),PokerCard(4,3),PokerCard(5,4),PokerCard(6,2)]))


