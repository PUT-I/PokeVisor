import argparse

import cv2

from chip_detector import chip_detection


def parse_arguments():
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False, help="path to image", default="chips_input.jpg")
    return vars(ap.parse_args())


# resize image while retaining aspect ratio
def resize_image(img, width):
    d = float(width) / img.shape[1]
    dim = (width, int(round(img.shape[0] * d)))
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


def main():
    args = parse_arguments()
    image = cv2.imread(args["image"])
    image = resize_image(image, 1080)

    # create a copy of the image to display results
    output = image.copy()

    chips = chip_detection.detect_chips(image, output)
    print(chips)

    # write summary on output image
    cv2.putText(output, "Chips detected: {}".format(len(chips)),
                (5, output.shape[0] - 24), cv2.FONT_HERSHEY_PLAIN,
                1.0, (0, 0, 255), lineType=cv2.LINE_AA)

    # show output and wait for key to terminate program
    cv2.imshow("Output", output)
    cv2.waitKey()


if __name__ == "__main__":
    main()
