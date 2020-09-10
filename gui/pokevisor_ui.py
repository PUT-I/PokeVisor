import tkinter.ttk as ttk
from time import sleep
from tkinter import *

from card_detector.classes.card_rank_enum import CardRank
from card_detector.classes.card_suit_enum import CardSuit
from card_detector.classes.poker_card import PokerCard
from chip_detector.classes.poker_chip_enum import PokerChip
from visualization.classes.player import Player

card_rank_symbols = {
    CardRank.two.name: "2",
    CardRank.three.name: "3",
    CardRank.four.name: "4",
    CardRank.five.name: "5",
    CardRank.six.name: "6",
    CardRank.seven.name: "7",
    CardRank.eight.name: "8",
    CardRank.nine.name: "9",
    CardRank.ten.name: "10",
    CardRank.jack.name: "J",
    CardRank.queen.name: "K",
    CardRank.king.name: "Q",
    CardRank.ace.name: "A"
}

card_suit_symbols = {
    CardSuit.spades.name: chr(9824),
    CardSuit.diamonds.name: chr(9830),
    CardSuit.hearts.name: chr(9829),
    CardSuit.clubs.name: chr(9827)
}


class PokeVisorUi(Tk):
    def __init__(self, players: int = 4):
        super().__init__(None)
        self.title('PokeVisor')
        self._initialize_table(players)

    def _initialize_table(self, players: int):
        community_cards_column1 = ttk.Entry(self, width=50)
        community_cards_column1.config({"background": "#97d8bc", "font": "bold"})
        community_cards_column1.grid(row=1, column=1, sticky=NSEW)
        community_cards_column1.insert(END, "Community Cards")

        self._game_stage = StringVar()
        community_cards_column2 = ttk.Entry(self, width=50, textvariable=self._game_stage)
        community_cards_column2.config({"background": "#dcf2e8", "font": "bold"})
        community_cards_column2.grid(row=1, column=2, sticky=NSEW)

        self._community_cards = StringVar()
        community_cards_column3 = ttk.Entry(self, width=50, textvariable=self._community_cards)
        community_cards_column3.config({"background": "#dcf2e8", "font": "bold"})
        community_cards_column3.grid(row=1, column=3, sticky=NSEW)

        self._player_cards_list = []
        self._player_chips_list = []
        for i in range(players):
            player_column1 = ttk.Entry(self, width=50)
            player_column1.config({"background": "#dcf2e8", "font": "bold"})
            player_column1.grid(row=i + 2, column=1, sticky=NSEW)
            player_column1.insert(END, "Player {}".format(i + 1))

            player_cards = StringVar()
            player_column2 = ttk.Entry(self, textvariable=player_cards)
            player_column2.config({"background": "#ffffff", "font": "bold"})
            player_column2.grid(row=i + 2, column=2, sticky=NSEW)

            player_chips = StringVar()
            player_column3 = ttk.Entry(self, textvariable=player_chips)
            player_column3.config({"background": "#ffffff", "font": "bold"})
            player_column3.grid(row=i + 2, column=3, sticky=NSEW)

            self._player_cards_list.append(player_cards)
            self._player_chips_list.append(player_chips)

    def write_turn(self, community_cards, list_of_players):
        cards_to_print = ""
        for card in community_cards:
            cards_to_print += card_rank_symbols[card.rank.name] + card_suit_symbols[card.suit.name] + ", "
            print(card.rank.name + " " + card.suit.name)
        self._community_cards.set(cards_to_print)

        if len(community_cards) == 0:
            self._game_stage.set("Preflop")
            print("preflop")
        elif len(community_cards) == 3:
            self._game_stage.set("Flop")
            print("flop")
            print("community cards")
        elif len(community_cards) == 4:
            self._game_stage.set("Turn")
            print("turn")
            print("community cards")
        elif len(community_cards) == 5:
            self._game_stage.set("River")
            print("river")
            print("community cards")

        for i in range(len(list_of_players)):
            print(list_of_players[i].name + "\n Cards:")

            player = list_of_players[i]
            cards = ""
            for card in player.cards:
                cards += "{}{}, ".format(card_rank_symbols[card.rank.name], card_suit_symbols[card.suit.name])
                print(card.rank.name + " " + card.suit.name)
            self._player_cards_list[i].set(cards)

            self._player_chips_list[i].set("has {} value in chips".format(player.sum_chip_values()))

            print("{} has {} value in chips".format(player.name, player.sum_chip_values()))
        self.update()


def main():
    card_1 = PokerCard(CardRank.ace, CardSuit.hearts)
    card_2 = PokerCard(CardRank.king, CardSuit.spades)
    card_3 = PokerCard(CardRank.nine, CardSuit.spades)
    community_cards = [card_1, card_2, card_3]
    hand_1 = [PokerCard(CardRank.five, CardSuit.spades), PokerCard(CardRank.five, CardSuit.clubs)]
    hand_2 = [PokerCard(CardRank.nine, CardSuit.diamonds), PokerCard(CardRank.nine, CardSuit.hearts)]
    hand_3 = [PokerCard(CardRank.jack, CardSuit.spades), PokerCard(CardRank.jack, CardSuit.clubs)]

    player_1 = Player("Player 1")
    player_1.chips[PokerChip.purple] = 1
    player_1.chips[PokerChip.red] = 6
    player_1.chips[PokerChip.red] = 6
    player_1.chips[PokerChip.green] = 8
    player_1.cards = hand_1

    player_2 = Player("Player 2")
    player_2.chips[PokerChip.purple] = 1
    player_2.chips[PokerChip.red] = 6
    player_2.chips[PokerChip.green] = 8
    player_2.cards = hand_2

    player_3 = Player("Player 3")
    player_3.chips[PokerChip.purple] = 1
    player_3.chips[PokerChip.red] = 6
    player_3.chips[PokerChip.green] = 8
    player_3.cards = hand_3

    poke_visor_ui = PokeVisorUi(3)
    poke_visor_ui.write_turn(community_cards, [player_1, player_2, player_3])

    print("Start of sleep")
    sleep(5)
    print("End of sleep")

    poke_visor_ui.write_turn(community_cards, [player_3, player_1, player_2])
    poke_visor_ui.mainloop()


if __name__ == "__main__":
    main()
