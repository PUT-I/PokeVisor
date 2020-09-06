import argparse
from math import cos, sin

import cv2
import numpy as np

from card_detector import card_detection

image = np.zeros((1, 1))


def parse_arguments():
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False, help="path to image", default="cards_input.png")
    ap.add_argument("-m", "--movie", required=False, help="path to movie", default="demo_movie.mp4")
    return vars(ap.parse_args())


def calculate_point(origin_point, angle, length):
    x = round(origin_point[0] + length * cos(angle * np.pi / 180.0))
    y = round(origin_point[1] + length * sin(angle * np.pi / 180.0))
    return x, y


def divide_table(img, players=4):
    height, width, _ = img.shape

    if width > height:
        length = width
    else:
        length = height

    center = (round(width / 2), round(height / 2))
    angular_step = 360 / players

    result = []
    for i in range(0, players):
        edge_point_1 = calculate_point(center, angular_step * i, length)
        edge_point_2 = calculate_point(center, angular_step * (i + 1), length)

        mask = np.zeros((height, width), np.uint8)

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

        gray = cv2.cvtColor(cutout, cv2.COLOR_BGR2GRAY)
        contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = contours[0]

        moments = cv2.moments(cnt)
        cutout_center = (round(moments["m10"] / moments["m00"]), round(moments["m01"] / moments["m00"]))
        cv2.putText(cutout, "Player {}".format(str(i + 1)),
                    cutout_center, cv2.FONT_HERSHEY_PLAIN,
                    2, (255, 0, 255), lineType=cv2.LINE_AA, thickness=2)

        result.append(cutout)
    return result


def supervise(frame, players=4):
    player_images = divide_table(frame, players)

    table_image = np.zeros(frame.shape, np.uint8)
    player_cards = []
    for i in range(len(player_images)):
        cards = card_detection.detect_cards(player_images[i], frame)
        player_cards.append(cards)
        table_image += player_images[i]

    return table_image, player_cards


def supervise_video(cap, players=4):
    fps = 60
    frame_time = round(1000 / fps)

    while cap.isOpened():
        ret, frame = cap.read()

        table, _ = supervise(frame, players)

        cv2.imshow('frame', table)
        if cv2.waitKey(frame_time) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


def image_example():
    global image

    args = parse_arguments()
    image = cv2.imread(args["image"])
    players = 4

    divided, _ = supervise(image, players)

    cv2.imshow("example", divided)

    def callback(players):
        global image

        if players < 2:
            players = 2

        table_image, _ = supervise(image, players)
        cv2.imshow("example", table_image)

    cv2.createTrackbar("players", "example", players, 8, callback)

    cv2.waitKey()
    cv2.destroyAllWindows()


def movie_example():
    args = parse_arguments()

    cap = cv2.VideoCapture(args["movie"])
    supervise_video(cap, players=2)
    cap.release()


def main():
    image_example()


if __name__ == "__main__":
    main()
