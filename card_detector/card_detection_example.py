#
# Based on: https://github.com/EdjeElectronics/OpenCV-Playing-Card-Detector
#
import argparse

import cv2

from card_detector import card_detection


def parse_arguments():
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False, help="path to image", default="cards_input.png")
    return vars(ap.parse_args())


def main():
    args = parse_arguments()

    image = cv2.imread(args["image"])
    cards = card_detection.detect_cards(image, image)

    print(cards)

    # Finally, display the image with the identified cards
    cv2.imshow("Card Detector", image)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
