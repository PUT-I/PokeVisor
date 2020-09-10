import argparse
import time
from typing import List

import cv2
import numpy as np

from classes.player import Player
from classes.poker_card import PokerCard
from gui.pokevisor_status_ui import PokeVisorStatusUi
from logic.card_detector import card_detection
from logic.chip_detector import chip_detection
from logic.game_supervisor import game_image_processing
from logic.hand_selecter.hand_checking import Checker

image = np.zeros((1, 1))


def supervise(frame: np.ndarray, dst: np.ndarray = None) -> tuple:
    community_image, player_images = game_image_processing.divide_table(frame)
    community_cards, community_cards_cnt = card_detection.detect_cards(community_image, dst)
    community_chips = chip_detection.detect_chips(community_image, dst, community_cards_cnt)

    player_cards_list = []
    player_chips_list = []
    for i in range(len(player_images)):
        cards, cards_cnt = card_detection.detect_cards(player_images[i], dst)
        chips = chip_detection.detect_chips(player_images[i], dst, cards_cnt)
        player_cards_list.append(sorted(cards))
        player_chips_list.append(chips)

    return sorted(community_cards), player_cards_list, community_chips, player_chips_list


def supervise_video(cap, players: int = 2) -> None:
    status_ui = PokeVisorStatusUi(players=players)
    fps = 60
    frame_time = round(1000 / fps)

    while cap.isOpened():
        start_time = time.time()
        ret, frame = cap.read()

        if not ret:
            break

        community_cards, player_cards_list, community_chips, player_chips_list = supervise(frame, dst=frame)

        table = game_image_processing.put_overlay_on_image(frame)
        if _check_if_cards_uncovered(community_cards, player_cards_list):
            player_list = _create_player_list(player_cards_list, player_chips_list, community_cards)
            status_ui.write_turn(community_cards, player_list)
        elif len([card for card in community_cards if card.is_unknown()]) == 0:
            status_ui.write_turn(community_cards, [])

        cv2.imshow('PokeVisor', table)
        duration = time.time() - start_time
        wait_time = round(frame_time - duration * 1000)
        if wait_time < 1:
            wait_time = 1
        if cv2.waitKey(wait_time) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    status_ui.destroy()
    cap.release()


def supervise_images(images: list, players: int = 2):
    status_ui = PokeVisorStatusUi(players=players)
    for image in images:
        community_cards, player_cards_list, community_chips, player_chips_list = supervise(image, dst=image)
        image = game_image_processing.put_overlay_on_image(image)

        player_list = _create_player_list(player_cards_list, player_chips_list, community_cards)
        status_ui.write_turn(community_cards, player_list)

        cv2.imshow("PokeVisor", image)
        cv2.waitKey()

    cv2.destroyAllWindows()
    status_ui.destroy()


def _create_player_list(player_cards_list, player_chips_list, community_cards):
    players = []
    for i in range(len(player_cards_list)):
        player = Player()
        player.cards = player_cards_list[i]
        player.chips = player_chips_list[i]
        player.hand = Checker.get_best_hand(player.cards, community_cards)
        players.append(player)
    return players


def _parse_arguments() -> vars:
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False, help="path to image", default="cards_input.png")
    ap.add_argument("-m", "--movie", required=False, help="path to movie", default="demo_movie.mp4")
    return vars(ap.parse_args())


def _check_if_cards_uncovered(community_cards: List[PokerCard], player_cards_list: List[List[PokerCard]]) -> bool:
    for card in community_cards:
        if card.is_unknown():
            return False

    for player_cards in player_cards_list:
        if len(player_cards) == 0:
            return False

        for card in player_cards:
            if card.is_unknown():
                return False

    print("Cards uncovered")
    return True


def _image_example():
    global image

    args = _parse_arguments()
    image = cv2.imread(args["image"])

    game_image_processing.setup(image)

    community_cards, player_cards_list, community_chips, player_chips_list = supervise(image, dst=image)

    print("Community cards: {}".format(community_cards))
    print("Community chips: {}".format([chip.name for chip in community_chips]))

    for i in range(len(player_cards_list)):
        print("Player {} cards: {}".format(i + 1, player_cards_list[i]))
        print("Player {} chips: {}".format(i + 1, [chip.name for chip in player_chips_list[i]]))

    image = game_image_processing.put_overlay_on_image(image)

    cv2.imshow("example", image)
    cv2.waitKey()
    cv2.destroyAllWindows()


def _video_example():
    args = _parse_arguments()

    cap = cv2.VideoCapture(args["movie"])

    _, frame = cap.read()

    game_image_processing.setup(frame, detect_chips=False)

    supervise_video(cap)
    cap.release()


def _main():
    _video_example()


if __name__ == "__main__":
    _main()
