from card_detector.classes.card_rank_enum import CardRank
from card_detector.classes.card_suit_enum import CardSuit
from card_detector.classes.poker_card import PokerCard
from hand_selector.classes.poker_hand_enum import PokerHand
from hand_selector.hand_checker import Checker
from visualization.classes.player import Player
from chip_detector.classes.poker_chip_enum import PokerChip
from tkinter import *


class TUI:
    @staticmethod
    def write__turn(community_cards, list_of_players):
        community_cards_row1 = Entry(relief=RIDGE, width=70)
        community_cards_row1.grid(row=1, column=1, sticky=NSEW)
        community_cards_row1.insert(END, "Community Cards")

        community_cards_row2 = Entry(relief=RIDGE, width=70)
        community_cards_row2.grid(row=1, column=2, sticky=NSEW)
        if len(community_cards) == 0:
            community_cards_row2.insert(END, "Preflop")
            print("preflop")
        elif len(community_cards) == 3:
            community_cards_row2.insert(END, "Flop")
            print("flop")
            print("community cards")
        elif len(community_cards) == 4:
            community_cards_row2.insert(END, "Turn")
            print("turn")
            print("community cards")
        elif len(community_cards) == 5:
            community_cards_row2.insert(END, "River")
            print("river")
            print("community cards")
        cards_to_print = ""
        for card in community_cards:
            cards_to_print += card.rank.name + " " + card.suit.name + ", "
            print(card.rank.name + " " + card.suit.name)
        community_cards_row3 = Entry(relief=RIDGE, width=70)
        community_cards_row3.grid(row=1, column=3, sticky=NSEW)
        community_cards_row3.insert(END, cards_to_print)

        for player in list_of_players:
            player_column1 = Entry(relief=RIDGE, width=70)
            player_column1.grid(row=list_of_players.index(player)+2, column=1, sticky=NSEW)
            player_column1.insert(END, player.name)

            print(player.name + "\n Cards:")
            cards = ""
            for card in player.cards:
                cards += card.rank.name + " " + card.suit.name + ", "
                print(card.rank.name + " " + card.suit.name)

            player_column2 = Entry(relief=RIDGE)
            player_column2.grid(row=list_of_players.index(player)+2, column=2, sticky=NSEW)
            player_column2.insert(END, cards)

            player_column3 = Entry(relief=RIDGE)
            player_column3.grid(row=list_of_players.index(player)+2, column=3, sticky=NSEW)
            player_column3.insert(END, "has {} value in chips".format(player.sum_chip_values()))

            print("{} has {} value in chips".format(player.name, player.sum_chip_values()))


def main():
    card_1 = PokerCard(CardRank.ace, CardSuit.hearts)
    card_2 = PokerCard(CardRank.king, CardSuit.spades)
    card_3 = PokerCard(CardRank.nine, CardSuit.spades)
    community_cards = [card_1, card_2, card_3]
    hand_1 = [PokerCard(CardRank.five, CardSuit.spades), PokerCard(CardRank.five, CardSuit.clubs)]
    hand_2 = [PokerCard(CardRank.nine, CardSuit.diamonds), PokerCard(CardRank.nine, CardSuit.clubs)]
    hand_3 = [PokerCard(CardRank.jack, CardSuit.spades), PokerCard(CardRank.jack, CardSuit.clubs)]
    player = Player("Player 1")

    player.chips[PokerChip.purple] = 1
    player.chips[PokerChip.red] = 6
    player.chips[PokerChip.red] = 6
    player.chips[PokerChip.green] = 8
    player.cards = hand_1

    player_1 = Player("Player 2")
    player_1.chips[PokerChip.purple] = 1
    player_1.chips[PokerChip.red] = 6
    player_1.chips[PokerChip.green] = 8
    player_1.cards = hand_2

    player_3 = Player("Player 3")
    player_3.chips[PokerChip.purple] = 1
    player_3.chips[PokerChip.red] = 6
    player_3.chips[PokerChip.green] = 8
    player_3.cards = hand_3
    TUI.write__turn(community_cards, [player, player_1, player_3])
    mainloop()


if __name__ == "__main__":
    main()
