import argparse
from math import cos, sin
from typing import Tuple, List

import cv2
import numpy as np

from card_detector import card_detection
from card_detector.classes.poker_card import PokerCard
from hand_selector.hand_checker import Checker

image = np.zeros((1, 1))


def _parse_arguments() -> vars:
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False, help="path to image", default="cards_input.png")
    ap.add_argument("-m", "--movie", required=False, help="path to movie", default="demo_movie.mp4")
    return vars(ap.parse_args())


def _calculate_point(origin_point: Tuple[int, int], angle: float, length: float) -> Tuple[int, int]:
    x = round(origin_point[0] + length * cos(angle * np.pi / 180.0))
    y = round(origin_point[1] + length * sin(angle * np.pi / 180.0))
    return x, y


def _process_cutout(img, center_text: str = "", draw_contour: bool = False) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]

    if draw_contour:
        for i in range(0, len(cnt)):
            point_1 = tuple(cnt[i][0])
            point_2 = tuple(cnt[(i + 1) % len(cnt)][0])
            cv2.line(img, point_1, point_2, (255, 0, 255), thickness=2)

    moments = cv2.moments(cnt)
    cutout_center = (round(moments["m10"] / moments["m00"]), round(moments["m01"] / moments["m00"]))
    cv2.putText(img, center_text, cutout_center, cv2.FONT_HERSHEY_PLAIN,
                2, (255, 0, 255), lineType=cv2.LINE_AA, thickness=2)

    return img


def _get_community_cards_cutout(img: np.ndarray, center_offset: int, round_cutout: bool = False) -> np.ndarray:
    height, width, _ = img.shape
    center = (round(width / 2), round(height / 2))

    comm_cards_img = np.zeros((height, width, 3), np.uint8)
    comm_cards_y1 = center[1] - center_offset
    comm_cards_y2 = center[1] + center_offset
    comm_cards_img[comm_cards_y1:comm_cards_y2, 0:width] = img[comm_cards_y1:comm_cards_y2, 0:width]
    img[comm_cards_y1:comm_cards_y2, 0:width] = (0, 0, 0)
    return comm_cards_img


def _get_player_cards_cutouts(img: np.ndarray, players: int) -> List[np.ndarray]:
    height, width, _ = img.shape

    if width > height:
        length = width
    else:
        length = height

    center = (round(width / 2), round(height / 2))
    angular_step = 360 / players

    result = []
    for i in range(0, players):
        edge_point_1 = _calculate_point(center, angular_step * i, length)
        edge_point_2 = _calculate_point(center, angular_step * (i + 1), length)

        mask = np.zeros((height, width), np.uint8)

        # Workarounds for specific cases
        if players == 2:
            if i == 0:
                corner_point_1 = (width - 1, 0)
                corner_point_2 = (0, 0)
            else:
                corner_point_1 = (0, height - 1)
                corner_point_2 = (width - 1, height - 1)
            points = np.array([[center, edge_point_1, corner_point_1, corner_point_2, edge_point_2]])
        elif players == 3 and i % 2 == 0:
            if i == 2:
                corner_point = (width - 1, 0)
            else:
                corner_point = (width - 1, height - 1)
            points = np.array([[center, edge_point_1, corner_point, edge_point_2]])
        else:
            points = np.array([[center, edge_point_1, edge_point_2]])
        cv2.fillPoly(mask, points, (255,))

        cutout = cv2.bitwise_and(img, img, mask=mask)
        _process_cutout(cutout, "")

        result.append(cutout)
    return result


def _divide_table(img: np.ndarray, players: int = 4, comm_cards_center_offset: int = 180) -> Tuple[
    np.ndarray, List[np.ndarray]]:
    community_image = _get_community_cards_cutout(img, comm_cards_center_offset)
    community_image = _process_cutout(community_image, "", draw_contour=True)
    player_images = _get_player_cards_cutouts(img, players)
    return community_image, player_images


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


def supervise(frame: np.ndarray, players: int = 4) -> Tuple[np.ndarray, List[PokerCard], List[List[PokerCard]]]:
    community_image, player_images = _divide_table(frame, players)
    community_cards = card_detection.detect_cards(community_image, frame)
    table_image = community_image

    player_cards_list = []
    for i in range(len(player_images)):
        cards = card_detection.detect_cards(player_images[i], frame)
        player_cards_list.append(cards)
        table_image += player_images[i]

    return table_image, community_cards, player_cards_list


def supervise_video(cap, players: int = 4) -> None:
    fps = 60
    frame_time = round(1000 / fps)

    while cap.isOpened():
        ret, frame = cap.read()

        table, community_cards, player_cards_list = supervise(frame, players)

        _check_if_cards_uncovered(community_cards, player_cards_list)

        cv2.imshow('frame', table)
        if cv2.waitKey(frame_time) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


def _image_example():
    global image

    args = _parse_arguments()
    image = cv2.imread(args["image"])
    players = 4

    divided, _, _ = supervise(image, players)

    cv2.imshow("example", divided)

    def callback(players):
        global image

        if players < 2:
            players = 2

        table_image, _, _ = supervise(image, players)
        cv2.imshow("example", table_image)

    cv2.createTrackbar("players", "example", players, 8, callback)

    cv2.waitKey()
    cv2.destroyAllWindows()


def _movie_example():
    args = _parse_arguments()

    cap = cv2.VideoCapture(args["movie"])
    supervise_video(cap, players=2)
    cap.release()


def _main():
    _movie_example()


if __name__ == "__main__":
    _main()
