from card_detector.classes.card_rank_enum import CardRank
from card_detector.classes.card_suit_enum import CardSuit
from card_detector.classes.poker_card import PokerCard
from hand_selector.classes.poker_hand_enum import PokerHand
from hand_selector.hand_checker import Checker
from visualization.classes.player import Player
from chip_detector.classes.poker_chip_enum import PokerChip

class TUI:
    @staticmethod
    def write__turn(community_cards,list_of_players):
        if len(community_cards)==0 :
           print("preflop")
        elif len(community_cards)==3:
            print("flop")
            print("community cards")
        elif len(community_cards)==4:
            print("turn")
            print("community cards")
        elif len(community_cards)==5:
            print("river")
            print("community cards")

       
        for card in community_cards:
            print(card.rank.name+" "+card.suit.name)

        for player in list_of_players:
            print(player.name+"\n Cards:")
            for card in player.cards:
                print(card.rank.name+" "+card.suit.name)
            print("Player {} has {} value in chips".format(player.name, player.sum_chip_values()))




def main():
    card_1 = PokerCard(CardRank.ace, CardSuit.hearts)
    card_2 = PokerCard(CardRank.king, CardSuit.spades)
    card_3 = PokerCard(CardRank.nine, CardSuit.spades)
    community_cards=[card_1,card_2,card_3]
    hand_1=[PokerCard(CardRank.five, CardSuit.spades),PokerCard(CardRank.five, CardSuit.clubs)]
    hand_2=[PokerCard(CardRank.nine, CardSuit.diamonds),PokerCard(CardRank.nine, CardSuit.clubs)]
    hand_3=[PokerCard(CardRank.jack, CardSuit.spades),PokerCard(CardRank.jack, CardSuit.clubs)]
    player = Player("Player 1")

    player.chips[PokerChip.purple] = 1
    player.chips[PokerChip.red] = 6
    player.chips[PokerChip.red] = 6
    player.chips[PokerChip.green] = 8
    player.cards=hand_1

    player_1 = Player("Player 2")
    player_1.chips[PokerChip.purple] = 1
    player_1.chips[PokerChip.red] = 6
    player_1.chips[PokerChip.green] = 8
    player_1.cards=hand_2

    player_3 = Player("Player 3")
    player_3.chips[PokerChip.purple] = 1
    player_3.chips[PokerChip.red] = 6
    player_3.chips[PokerChip.green] = 8
    player_3.cards=hand_3
    TUI.write__turn(community_cards,[player,player_1,player_3])


if __name__ == "__main__":
    main()
