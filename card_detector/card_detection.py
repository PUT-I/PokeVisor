#
# Based on: https://github.com/EdjeElectronics/OpenCV-Playing-Card-Detector
#
import os
from typing import List

import cv2

from card_detector import card_detection_functions
# Define font to use
from card_detector.classes.poker_card_info import PokerCardInfo

font = cv2.FONT_HERSHEY_SIMPLEX

# Load the train rank and suit images
path = os.path.dirname(os.path.abspath(__file__))
train_ranks = card_detection_functions.load_ranks(path + "/sample_images/")
train_suits = card_detection_functions.load_suits(path + "/sample_images/")


def detect_cards(image, dst=None) -> list:
    # Pre-process camera image (gray, blur, and threshold it)
    pre_proc = card_detection_functions.preprocess_image(image)

    # Find and sort the contours of all cards in the image (poker cards)
    cnts_sort, cnt_is_card = card_detection_functions.find_cards(pre_proc)

    # Initialize a new "cards" list to store the card objects.
    cards: List[PokerCardInfo] = []

    # If there are no contours, do nothing
    if len(cnts_sort) != 0:

        # Initialize a new "cards" list to assign the card objects.
        # k indexes the newly made array of cards.
        k = 0

        # For each contour detected:
        for i in range(len(cnts_sort)):
            image_cnt = cv2.drawContours(image.copy(), cnts_sort[i], -1, (0, 255, 0), thickness=10)
            size = cv2.contourArea(cnts_sort[i])
            cv2.putText(image_cnt, str(size), (0, 100),
                        cv2.FONT_HERSHEY_PLAIN,
                        1.5, (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

            if cnt_is_card[i] == 1:
                # Create a card object from the contour and append it to the list of cards.
                # preprocess_card function takes the card contour and contour and
                # determines the cards properties (corner points, etc). It generates a
                # flattened 200x300 image of the card, and isolates the card"s
                # suit and rank from the image.
                cards.append(card_detection_functions.preprocess_card(cnts_sort[i], image))

                # Find the best rank and suit match for the card.
                cards[k].best_rank_match, cards[k].best_suit_match, cards[k].rank_diff, cards[
                    k].suit_diff = card_detection_functions.match_card(cards[k], train_ranks, train_suits)

                # Draw center point and match result on the image.
                image = card_detection_functions.draw_results(image, cards[k])
                k = k + 1

        # Draw card contours on image (have to do contours all at once or
        # they do not show up properly for some reason)
        if dst is not None:
            if len(cards) != 0:
                temp_cnts = []
                for i in range(len(cards)):
                    temp_cnts.append(cards[i].contour)
                cv2.drawContours(image, temp_cnts, -1, (255, 0, 0), 2)
    return [card.to_poker_card() for card in cards]
