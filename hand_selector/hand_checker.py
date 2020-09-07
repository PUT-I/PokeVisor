from poker_card import PokerCard
from collections import defaultdict




## hand is best 5 cards

class Checker:
    def check_hand(hand):
        if Checker.royal_flush(hand):
            return 9
        if Checker.check_four_of_a_kind(hand):
            return 8
        if Checker.check_full_house(hand):
            return 7
        if Checker.check_color(hand):
            return 6
        if Checker.check_straight(hand):
            return 5
        if Checker.check_three_of_a_kind(hand):
            return 4
        if Checker.check_two_pair(hand):
            return 3
        if Checker.check_pair(hand):
            return 2
        return 1






    def royal_flush(hand):
        if Checker.check_color(hand) and Checker.check_straight(hand):
            return True
        else:
            return False


    def check_four_of_a_kind(hand):
        values = hand
        dic = defaultdict(int)
        for v in values:
            dic[v.rank]+=1
        if 4 in dic.values():
            return True
        else:
            return False
    

    def check_full_house(hand):
        values = hand
        dic = defaultdict(int)
        for v in values:
            dic[v.rank]+=1
        if sorted(dic.values())==[2,3]:
            return True
        else:
            return False   







    def check_color(hand):
        values = hand
        dic = defaultdict(int)
        for v in values:
            dic[v.suit]+=1
        if 5 in dic.values():
            return True
        else:
            return False


    def check_straight(hand):
        values = hand
        dic = defaultdict(int)
        for v in values:
            dic[v.rank]+=1
        sorted_dic=sorted(dic.keys())
        lowest_card=sorted_dic[0]
        if len(sorted_dic)==5:
            if (sorted_dic[1]==lowest_card+1 and sorted_dic[2]==lowest_card+2 and sorted_dic[3]==lowest_card+3 and sorted_dic[4]==lowest_card+4):
                return True
            elif sorted_dic==[1,10,11,12,13]:
                return True
            else:
                return False
        else:
            return False


    def check_three_of_a_kind(hand):
        values = hand
        dic = defaultdict(int)
        for v in values:
            dic[v.rank]+=1
        if 3 in dic.values():
            return True
        else:
            return False
    


    def check_two_pair(hand):
        values = hand
        dic = defaultdict(int)
        for v in values:
            dic[v.rank]+=1
        if sorted(dic.values())==[1,2,2]:
            return True
        else:
            return False



    def check_pair(hand):
        values = hand
        dic = defaultdict(int)
        for v in values:
            dic[v.rank]+=1
        if 2 in dic.values():
            return True
        else:
            return False



hand = [PokerCard(1,3),PokerCard(5,4),PokerCard(2,3),PokerCard(3,3),PokerCard(4,3)]
print(Checker.check_straight(hand))

