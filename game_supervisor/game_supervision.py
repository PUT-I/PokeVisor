import argparse
from typing import Tuple, List

import cv2
import numpy as np

from card_detector import card_detection
from card_detector.classes.poker_card import PokerCard
from game_supervisor import game_image_processing
from hand_selector.hand_checker import Checker

image = np.zeros((1, 1))


def supervise(frame: np.ndarray, dst: np.ndarray = None) -> Tuple[List[PokerCard], List[List[PokerCard]]]:
    community_image, player_images = game_image_processing.divide_table(frame)
    community_cards = card_detection.detect_cards(community_image, dst)

    player_cards_list = []
    for i in range(len(player_images)):
        cards = card_detection.detect_cards(player_images[i], dst)
        player_cards_list.append(cards)

    return community_cards, player_cards_list


def supervise_video(cap) -> None:
    fps = 60
    frame_time = round(1000 / fps)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        community_cards, player_cards_list = supervise(frame, dst=frame)

        table = game_image_processing.put_overlay_on_image(frame)
        _check_if_cards_uncovered(community_cards, player_cards_list)

        cv2.imshow('frame', table)
        if cv2.waitKey(frame_time) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


def _parse_arguments() -> vars:
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False, help="path to image", default="cards_input.png")
    ap.add_argument("-m", "--movie", required=False, help="path to movie", default="demo_movie.mp4")
    return vars(ap.parse_args())


def _check_if_cards_uncovered(community_cards: List[PokerCard], player_cards_list: List[List[PokerCard]]) -> None:
    for card in community_cards:
        if card.is_unknown():
            return

    for player_cards in player_cards_list:
        if len(player_cards) == 0:
            return

        for card in player_cards:
            if card.is_unknown():
                return

    print("Cards uncovered")
    player_num = 1
    for player_cards in player_cards_list:
        hand = Checker.get_best_hand(player_cards, community_cards)
        print("Player {} has {}".format(player_num, hand.name))
        player_num += 1


def _image_example():
    global image

    args = _parse_arguments()
    image = cv2.imread(args["image"])

    game_image_processing.setup(image)

    _, _ = supervise(image, dst=image)

    cv2.imshow("example", image)
    cv2.waitKey()
    cv2.destroyAllWindows()


def _movie_example():
    args = _parse_arguments()

    cap = cv2.VideoCapture(args["movie"])

    _, frame = cap.read()

    game_image_processing.setup(frame)

    supervise_video(cap)
    cap.release()


def _main():
    _movie_example()


if __name__ == "__main__":
    _main()
