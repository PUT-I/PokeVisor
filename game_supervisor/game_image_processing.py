from math import cos, sin
from typing import Tuple, List

import cv2
import numpy as np

_community_mask = None
_player_masks = []
_description_mask = None
_description_overlay = None
_players = 4
_community_cards_offset = 180


def divide_table(img):
    global _community_mask, _player_masks

    community_image = cv2.bitwise_and(img, img, mask=_community_mask)
    player_images = []
    for player_mask in _player_masks:
        player_images.append(cv2.bitwise_and(img, img, mask=player_mask))
    return community_image, player_images


def put_overlay_on_image(img):
    global _description_overlay, _description_mask

    img_result = img.copy()
    img_result = cv2.bitwise_and(img_result, img_result, mask=_description_mask)
    img_result = cv2.add(img_result, _description_overlay)

    return img_result


def setup(img):
    def _common_callback():
        global _players, _community_cards_offset

        _setup_masks(img, players=_players, comm_cards_center_offset=_community_cards_offset)

        img_temp = put_overlay_on_image(img)

        cv2.imshow("setup", img_temp)

    def _players_callback(players):
        global _players

        if players < 2:
            return

        _players = players
        _common_callback()

    def _offset_callback(offset):
        global _community_cards_offset

        if offset < 10:
            return

        _community_cards_offset = offset
        _common_callback()

    cv2.imshow("setup", img)
    cv2.createTrackbar("players", "setup", 2, 8, _players_callback)

    max_offset = round(img.shape[0] / 4)
    default_offset = round(img.shape[0] / 8)
    cv2.createTrackbar("community cards offset", "setup", default_offset, max_offset, _offset_callback)
    _players_callback(2)
    _offset_callback(default_offset)

    while cv2.waitKey() != ord("s"):
        pass
    cv2.destroyAllWindows()


def _calculate_point(origin_point: Tuple[int, int], angle: float, length: float) -> Tuple[int, int]:
    x = round(origin_point[0] + length * cos(angle * np.pi / 180.0))
    y = round(origin_point[1] + length * sin(angle * np.pi / 180.0))
    return x, y


def _process_cutout(cutout, dst, center_text: str = "", draw_contour: bool = False) -> None:
    contours, hierarchy = cv2.findContours(cutout, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]

    if draw_contour:
        for i in range(0, len(cnt)):
            point_1 = tuple(cnt[i][0])
            point_2 = tuple(cnt[(i + 1) % len(cnt)][0])
            cv2.line(dst, point_1, point_2, (255, 0, 255), thickness=2)

    moments = cv2.moments(cnt)
    cutout_center = (round(moments["m10"] / moments["m00"]), round(moments["m01"] / moments["m00"]))
    cv2.putText(dst, center_text, cutout_center, cv2.FONT_HERSHEY_PLAIN,
                2, (255, 0, 255), lineType=cv2.LINE_AA, thickness=2)


def _get_community_cards_cutout(img: np.ndarray, center_offset: int, round_cutout: bool = False) -> np.ndarray:
    height, width, _ = img.shape
    center = (round(width / 2), round(height / 2))

    comm_cards_img = np.zeros((height, width, 3), np.uint8)

    if round_cutout:
        comm_cards_img = cv2.circle(comm_cards_img, center, center_offset, 255, -1)
    else:
        comm_cards_y1 = center[1] - center_offset
        comm_cards_y2 = center[1] + center_offset
        comm_cards_img[comm_cards_y1:comm_cards_y2, 0:width] = img[comm_cards_y1:comm_cards_y2, 0:width]

    gray = cv2.cvtColor(comm_cards_img, cv2.COLOR_BGR2GRAY)
    _, comm_cards_mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    return comm_cards_mask


def _get_player_cards_cutouts(img: np.ndarray, players: int, community_mask=None) -> List[np.ndarray]:
    height, width, _ = img.shape

    # Remove references to original images
    community_mask = community_mask.copy()

    if community_mask is not None:
        community_mask = cv2.bitwise_not(community_mask)

    if width > height:
        length = width
    else:
        length = height

    center = (round(width / 2), round(height / 2))
    angular_step = 360 / players

    player_masks = []
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

        if community_mask is not None:
            mask = cv2.bitwise_and(mask, mask, mask=community_mask)

        player_masks.append(mask)

    return player_masks


def _setup_masks(img: np.ndarray, players: int = 4, comm_cards_center_offset: int = 180) -> None:
    global _community_mask, _player_masks, _description_overlay, _description_mask

    round_community_cutout = False
    if players > 2:
        round_community_cutout = True

    _community_mask = _get_community_cards_cutout(img, comm_cards_center_offset, round_community_cutout)
    _player_masks = _get_player_cards_cutouts(img, players, community_mask=_community_mask)

    _description_overlay = np.zeros(img.shape, np.uint8)

    _process_cutout(_community_mask, _description_overlay, "Community cards", draw_contour=True)

    player_num = 1
    for player_mask in _player_masks:
        _process_cutout(player_mask, _description_overlay, "Player {}".format(player_num), draw_contour=True)
        player_num += 1

    _description_mask = cv2.cvtColor(_description_overlay, cv2.COLOR_BGR2GRAY)
    _, _description_mask = cv2.threshold(_description_mask, 1, 255, cv2.THRESH_BINARY_INV)
