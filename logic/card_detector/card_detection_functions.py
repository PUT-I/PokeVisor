#
# Based on: https://github.com/EdjeElectronics/OpenCV-Playing-Card-Detector
#
import json
import os

import cv2
import numpy as np

from classes.card_detector.poker_card_info import PokerCardInfo
from classes.card_detector.train_ranks import TrainRanks
from classes.card_detector.train_suits import TrainSuits
# Adaptive threshold levels
from enums.card_rank_enum import CardRank
from enums.card_suit_enum import CardSuit

# Constants #

BKG_THRESH = 70
CARD_THRESH = 30

# Width and height of card corner, where rank and suit are
CORNER_WIDTH = 64
CORNER_HEIGHT = 160

# Dimensions of rank train images
RANK_WIDTH = 70
RANK_HEIGHT = 125

# Dimensions of suit train images
SUIT_WIDTH = 70
SUIT_HEIGHT = 100

RANK_DIFF_MAX = 2000
SUIT_DIFF_MAX = 700

CARD_MAX_AREA = 240000
CARD_MIN_AREA = 12500

font = cv2.FONT_HERSHEY_SIMPLEX


def _load_settings():
    global CARD_MAX_AREA, CARD_MIN_AREA

    if os.path.isfile("config.json"):
        with open("config.json", "r") as file:
            settings = json.loads(file.read())["card-detector"]
        CARD_MAX_AREA = settings["card-max-area"]
        CARD_MIN_AREA = settings["card-min-area"]


_load_settings()


def load_ranks(filepath):
    """Loads rank images from directory specified by filepath. Stores
    them in a list of Train_ranks objects."""

    train_ranks = []

    for rank in CardRank:
        if rank == CardRank.unknown:
            continue

        train_ranks.append(TrainRanks())
        last = len(train_ranks) - 1
        train_ranks[last].rank = rank
        filename = str(rank.name) + ".jpg"
        train_ranks[last].img = cv2.imread(filepath + filename, cv2.IMREAD_GRAYSCALE)

    return train_ranks


def load_suits(filepath):
    """Loads suit images from directory specified by filepath. Stores
    them in a list of Train_suits objects."""

    train_suits = []

    for suit in CardSuit:
        if suit == CardSuit.unknown:
            continue

        train_suits.append(TrainSuits())
        last = len(train_suits) - 1
        train_suits[last].suit = suit
        filename = str(suit.name) + ".jpg"
        train_suits[last].img = cv2.imread(filepath + filename, cv2.IMREAD_GRAYSCALE)

    return train_suits


def preprocess_image(image):
    """Returns a grayed, blurred, and adaptively thresholded camera image."""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 5, 2)
    return thresh


def find_cards(thresh_image):
    """Finds all card-sized contours in a thresholded camera image.
    Returns the number of cards, and a list of card contours sorted
    from largest to smallest."""

    # Find contours and sort their indices by contour size
    cnts, hier = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    index_sort = sorted(range(len(cnts)), key=lambda i: cv2.contourArea(cnts[i]), reverse=True)

    # If there are no contours, do nothing
    if len(cnts) == 0:
        return [], []

    # Otherwise, initialize empty sorted contour and hierarchy lists
    cnts_sort = []
    hier_sort = []
    cnt_is_card = np.zeros(len(cnts), dtype=int)

    # Fill empty lists with sorted contour and sorted hierarchy. Now,
    # the indices of the contour list still correspond with those of
    # the hierarchy list. The hierarchy array can be used to check if
    # the contours have parents or not.
    for i in index_sort:
        cnts_sort.append(cnts[i])
        hier_sort.append(hier[0][i])

    # Determine which of the contours are cards by applying the
    # following criteria: 1) Smaller area than the maximum card size,
    # 2), bigger area than the minimum card size, 3) have no parents,
    # and 4) have four corners

    for i in range(len(cnts_sort)):
        size = cv2.contourArea(cnts_sort[i])
        peri = cv2.arcLength(cnts_sort[i], True)
        approx = cv2.approxPolyDP(cnts_sort[i], 0.01 * peri, True)

        if CARD_MAX_AREA > size > CARD_MIN_AREA and len(approx) == 4:
            cnt_is_card[i] = 1

    return cnts_sort, cnt_is_card


def preprocess_card(contour, image) -> PokerCardInfo:
    """Uses contour to find information about the poker card. Isolates rank
    and suit images from the card."""

    # Initialize new card_info object
    card_info = PokerCardInfo()

    card_info.contour = contour

    # Find perimeter of card and use it to approximate corner points
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.01 * peri, True)
    pts = np.float32(approx)

    # Find width and height of card"s bounding rectangle
    x, y, w, h = cv2.boundingRect(contour)
    card_info.width, card_info.height = w, h

    # Find center point of card by taking x and y average of the four corners.
    average = np.sum(pts, axis=0) / len(pts)
    cent_x = int(average[0][0])
    cent_y = int(average[0][1])
    card_info.center = [cent_x, cent_y]

    # Warp card into 256x360 flattened image using perspective transform
    warp = cv2.resize(_flattener(image, pts, w, h), (256, 360))

    # Grab corner of warped card image and do a 4x zoom
    corner = warp[0:CORNER_HEIGHT, 0:CORNER_WIDTH]
    corner_zoom = cv2.resize(corner, (0, 0), fx=4, fy=4)

    # Sample known white pixel intensity to determine good threshold level
    white_level = corner_zoom[corner_zoom.shape[0] - 1, int((CORNER_WIDTH * 4) / 2)]
    thresh_level = white_level - CARD_THRESH
    if thresh_level <= 0:
        thresh_level = 1
    _, poker_thresh = cv2.threshold(corner_zoom, thresh_level, 255, cv2.THRESH_BINARY_INV)

    # Split in to top and bottom half (top shows rank, bottom shows suit)
    rank = poker_thresh[0:round(CORNER_HEIGHT * 2), 0:CORNER_WIDTH * 4]
    suit = poker_thresh[round(CORNER_HEIGHT * 2):CORNER_HEIGHT * 4, 0:CORNER_WIDTH * 4]

    # Find rank contour and bounding rectangle, isolate and find largest contour
    rank_cnts, hier = cv2.findContours(rank, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rank_cnts = sorted(rank_cnts, key=cv2.contourArea, reverse=True)

    # Find bounding rectangle for largest contour, use it to resize poker rank
    # image to match dimensions of the train rank image
    if len(rank_cnts) != 0:
        x1, y1, w1, h1 = cv2.boundingRect(rank_cnts[0])
        rank_roi = rank[y1:y1 + h1, x1:x1 + w1]
        rank_sized = cv2.resize(rank_roi, (RANK_WIDTH, RANK_HEIGHT), 0, 0)
        card_info.rank_img = rank_sized

    # Find suit contour and bounding rectangle, isolate and find largest contour
    suit_cnts, hier = cv2.findContours(suit, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    suit_cnts = sorted(suit_cnts, key=cv2.contourArea, reverse=True)

    # Find bounding rectangle for largest contour, use it to resize poker suit
    # image to match dimensions of the train suit image
    if len(suit_cnts) != 0:
        x2, y2, w2, h2 = cv2.boundingRect(suit_cnts[0])
        suit_roi = suit[y2:y2 + h2, x2:x2 + w2]
        suit_sized = cv2.resize(suit_roi, (SUIT_WIDTH, SUIT_HEIGHT), 0, 0)
        card_info.suit_img = suit_sized

    return card_info


def match_card(card, train_ranks, train_suits):
    """Finds best rank and suit matches for the poker card. Differences
    the poker card rank and suit images with the train rank and suit images.
    The best match is the rank or suit image that has the least difference."""

    best_rank_match_diff = 10000
    best_suit_match_diff = 10000
    best_rank_match_name = CardRank.unknown
    best_suit_match_name = CardSuit.unknown
    best_rank_name = CardRank.unknown
    best_suit_name = CardSuit.unknown

    # If no contours were found in poker card in preprocess_card function,
    # the img size is zero, so skip the differencing process
    # (card will be left as unknown)
    if (len(card.rank_img) != 0) and (len(card.suit_img) != 0):

        # Difference the poker card rank image from each of the train rank images,
        # and store the result with the least difference
        for t_rank in train_ranks:

            diff_img = cv2.absdiff(card.rank_img, t_rank.img)
            rank_diff = int(np.sum(diff_img) / 255)

            if rank_diff < best_rank_match_diff:
                best_rank_match_diff = rank_diff
                best_rank_name = t_rank.rank

        # Same process with suit images
        for t_suit in train_suits:

            diff_img = cv2.absdiff(card.suit_img, t_suit.img)
            suit_diff = int(np.sum(diff_img) / 255)

            if suit_diff < best_suit_match_diff:
                best_suit_match_diff = suit_diff
                best_suit_name = t_suit.suit

    # Combine best rank match and best suit match to get poker card"s identity.
    # If the best matches have too high of a difference value, card identity
    # is still unknown
    if best_rank_match_diff < RANK_DIFF_MAX:
        best_rank_match_name = best_rank_name

    if best_suit_match_diff < SUIT_DIFF_MAX:
        best_suit_match_name = best_suit_name

    # Return the identity of the card and the quality of the suit and rank match
    return best_rank_match_name, best_suit_match_name, best_rank_match_diff, best_suit_match_diff


def draw_results(image, card):
    """Draw the card name and contour on the camera image."""

    x = card.center[0]
    y = card.center[1]

    rank_name = card.best_rank_match
    suit_name = card.best_suit_match

    # Draw card name twice, so letters have black outline
    cv2.putText(image, (rank_name.name + " of"), (x - 60, y - 10), font, 1, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(image, (rank_name.name + " of"), (x - 60, y - 10), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.putText(image, suit_name.name, (x - 60, y + 25), font, 1, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(image, suit_name.name, (x - 60, y + 25), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    return image


def _flattener(image, pts, w, h):
    """Flattens an image of a card into a top-down 200x300 perspective.
    Returns the flattened, re-sized, grayed image.
    See www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/"""
    temp_rect = np.zeros((4, 2), dtype="float32")

    s = np.sum(pts, axis=2)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis=-1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    # Need to create an array listing points in order of
    # [top left, top right, bottom right, bottom left]
    # before doing the perspective transform

    if w <= 0.8 * h:  # If card is vertically oriented
        temp_rect[0] = tl
        temp_rect[1] = tr
        temp_rect[2] = br
        temp_rect[3] = bl

    if w >= 1.2 * h:  # If card is horizontally oriented
        temp_rect[0] = bl
        temp_rect[1] = tl
        temp_rect[2] = tr
        temp_rect[3] = br

    # If the card is "diamond" oriented, a different algorithm
    # has to be used to identify which point is top left, top right
    # bottom left, and bottom right.

    if 0.8 * h < w < 1.2 * h:  # If card is diamond oriented
        # If furthest left point is higher than furthest right point,
        # card is tilted to the left.
        if pts[1][0][1] <= pts[3][0][1]:
            # If card is titled to the left, approxPolyDP returns points
            # in this order: top right, top left, bottom left, bottom right
            temp_rect[0] = pts[1][0]  # Top left
            temp_rect[1] = pts[0][0]  # Top right
            temp_rect[2] = pts[3][0]  # Bottom right
            temp_rect[3] = pts[2][0]  # Bottom left

        # If furthest left point is lower than furthest right point,
        # card is tilted to the right
        if pts[1][0][1] > pts[3][0][1]:
            # If card is titled to the right, approxPolyDP returns points
            # in this order: top left, bottom left, bottom right, top right
            temp_rect[0] = pts[0][0]  # Top left
            temp_rect[1] = pts[3][0]  # Top right
            temp_rect[2] = pts[2][0]  # Bottom right
            temp_rect[3] = pts[1][0]  # Bottom left

    max_width = 200
    max_height = 300

    # Create destination array, calculate perspective transform matrix,
    # and warp card image
    dst = np.array([[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]], np.float32)
    m = cv2.getPerspectiveTransform(temp_rect, dst)
    warp = cv2.warpPerspective(image, m, (max_width, max_height))
    warp = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)

    return warp
