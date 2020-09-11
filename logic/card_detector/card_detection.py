#
# Based on: https://github.com/EdjeElectronics/OpenCV-Playing-Card-Detector
#
import os
from typing import List

import cv2
import numpy as np

# Define font to use
from classes.card_detector.poker_card_info import PokerCardInfo
from logic.card_detector import card_detection_functions

font = cv2.FONT_HERSHEY_SIMPLEX

# Load the train rank and suit images
path = os.getcwd()
train_ranks = card_detection_functions.load_ranks(path + "/sample_images/")
train_suits = card_detection_functions.load_suits(path + "/sample_images/")


def _remove_non_card_contours(cnts_sort: list, cnt_is_card: np.ndarray):
    cnts_sort_result = cnts_sort

    non_card_contours = []
    for i in range(0, len(cnts_sort_result)):
        if cnt_is_card[i] != 1:
            non_card_contours.append(i)

    cnt_is_card = np.delete(cnt_is_card, non_card_contours, None)
    for index in sorted(non_card_contours, reverse=True):
        cnts_sort_result.pop(index)

    return cnts_sort_result, cnt_is_card


def _remove_inclusive_contours(cnts_sort: list, cnt_is_card: np.ndarray):
    contour_removed = True
    cnts_sort_result = cnts_sort

    while contour_removed:
        contour_removed = False
        for i in range(len(cnts_sort_result)):
            for j in range(0, len(cnts_sort_result)):
                if j == i:
                    continue

                all_points_inside = True
                for point in cnts_sort_result[i]:
                    dist = cv2.pointPolygonTest(cnts_sort[j], tuple(point[0]), False)
                    if dist < 0:
                        all_points_inside = False
                        break

                if all_points_inside:
                    cnts_sort.pop(i)
                    cnt_is_card = np.delete(cnt_is_card, i)
                    contour_removed = True
                    break
            if contour_removed:
                break
    return cnts_sort_result, cnt_is_card


def detect_cards(image, dst=None) -> tuple:
    # Pre-process camera image (gray, blur, and threshold it)
    pre_proc = card_detection_functions.preprocess_image(image)

    # Find and sort the contours of all cards in the image (poker cards)
    cnts_sort, cnt_is_card = card_detection_functions.find_cards(pre_proc)

    if not np.any(cnt_is_card):
        return [], []

    cnts_sort, cnt_is_card = _remove_non_card_contours(cnts_sort, cnt_is_card)
    cnts_sort, cnt_is_card = _remove_inclusive_contours(cnts_sort, cnt_is_card)

    # Initialize a new "cards" list to store the card objects.
    cards: List[PokerCardInfo] = []

    # If there are no contours, do nothing
    if len(cnts_sort) != 0:

        # Initialize a new "cards" list to assign the card objects.
        # k indexes the newly made array of cards.
        k = 0

        # For each contour detected:
        for i in range(len(cnts_sort)):
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
            if dst is not None:
                dst = card_detection_functions.draw_results(dst, cards[k])
            k = k + 1

        # Draw card contours on image (have to do contours all at once or
        # they do not show up properly for some reason)
        if dst is not None:
            if len(cards) != 0:
                temp_cnts = []
                for i in range(len(cards)):
                    temp_cnts.append(cards[i].contour)
                cv2.drawContours(dst, temp_cnts, -1, (255, 0, 0), 2)
    return [card.to_poker_card() for card in cards], [card.contour for card in cards]
