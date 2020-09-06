#
# Based on: https://github.com/EdjeElectronics/OpenCV-Playing-Card-Detector
#
import argparse

import cv2

from card_detector import card_detection


def parse_arguments():
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--movie", required=False, help="path to movie", default="demo_movie.mp4")
    return vars(ap.parse_args())


def main():
    args = parse_arguments()

    cap = cv2.VideoCapture(args["movie"])
    fps = 30
    frame_time = round(1000 / fps)

    while cap.isOpened():
        ret, frame = cap.read()

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        cards = card_detection.detect_cards(frame, frame)

        cv2.imshow('frame', frame)
        print(cards)
        if cv2.waitKey(frame_time) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
