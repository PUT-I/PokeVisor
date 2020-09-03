#
# Based on: https://github.com/EdjeElectronics/OpenCV-Playing-Card-Detector
#

import cv2

from card_detector import card_detection


def main():
    image = cv2.imread('cards_input.png')
    cards = card_detection.detect_cards(image, image)

    print(cards)

    # Finally, display the image with the identified cards
    cv2.imshow('Card Detector', image)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
