import glob
import json
import os
from typing import Optional, List

import cv2
import numpy as np
from joblib import dump, load
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from enums.poker_chip_enum import PokerChip

# noinspection PyTypeChecker
_clf: MLPClassifier = None
_enabled = True

CHIP_MIN_DISTANCE = 100
CHIP_MIN_RADIUS = 20
CHIP_MAX_RADIUS = 120


def _load_settings():
    global CHIP_MIN_RADIUS, CHIP_MAX_RADIUS, CHIP_MIN_DISTANCE

    if os.path.isfile("config.json"):
        with open("config.json", "r") as file:
            settings = json.loads(file.read())["chip-detector"]
        CHIP_MIN_DISTANCE = settings["chip-min-distance"]
        CHIP_MIN_RADIUS = settings["chip-min-radius"]
        CHIP_MAX_RADIUS = settings["chip-max-radius"]


_load_settings()


def disable():
    global _enabled
    _enabled = False


def setup(classifier_path: str = "chip_classifier.joblib"):
    global _clf

    _clf = _load_classifier(classifier_path)
    if _clf is None:
        input_data, output_data = _create_training_data_sets("sample_images")
        _clf, _ = _train_classifier(input_data, output_data, classifier_path)


def generate_classifier(sample_images_path: str, output_filename: str):
    if not os.path.isdir(sample_images_path):
        raise FileNotFoundError

    input_data, output_data = _create_training_data_sets(sample_images_path)

    if not input_data or not output_data:
        raise FileNotFoundError

    _, _ = _train_classifier(input_data, output_data, output_filename)


def detect_chips(img, dst=None, card_cnts: list = None) -> List[PokerChip]:
    global _clf, _enabled

    if not _enabled:
        return []

    # convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # improve contrast accounting for differences in lighting conditions:
    # create a CLAHE object to apply contrast limiting adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    circles = _detect_circles(gray)

    if circles is None:
        return []

    if card_cnts is not None:
        circles = _remove_circles_in_contour(circles, card_cnts)

    poker_chips = _predict_chips(hsv_img, _clf, circles, dst=dst)

    return poker_chips


def _remove_circles_in_contour(circles: list, cnts: list):
    circles_to_remove = []
    for i in range(len(circles[0])):
        x, y, d = circles[0][i]
        for cnt in cnts:
            points = [(x, y), (x + d, y), (x - d, y), (x, y + d), (x, y - d)]
            circle_in_cnts = False

            for point in points:
                dist = cv2.pointPolygonTest(cnt, point, False)
                if dist >= 0:
                    circle_in_cnts = True
                    break
            if circle_in_cnts:
                circles_to_remove.append(i)
                break
    if len(circles_to_remove) == 0:
        return circles

    circles_temp = np.delete(circles[0], circles_to_remove, axis=0)
    circles_result = np.empty((1,) + circles_temp.shape)
    circles_result[0] = circles_temp
    return circles_result


def _calc_histogram(hsv_img):
    # hsv_img = cv2.resize(hsv_img, (128, 128))

    # create mask
    m = np.zeros(hsv_img.shape[:2], dtype="uint8")
    (w, h) = (int(hsv_img.shape[1] / 2), int(hsv_img.shape[0] / 2))
    m = cv2.circle(m, (w, h), 60, 255, -1)

    # calcHist expects a list of images, color channels, mask, bins, ranges
    h = cv2.calcHist([hsv_img], [0, 1], m, [180, 255], [0, 180, 0, 255])

    # return normalized "flattened" histogram
    return cv2.normalize(h, h).flatten()


def _calc_hist_from_file(file):
    img = cv2.imread(file)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return _calc_histogram(img)


def _create_training_data_sets(sample_images_path: str):
    # locate sample image files
    sample_images = []
    for enum in PokerChip:
        sample_images.append(
            (enum, glob.glob("{}/{}/*".format(sample_images_path, enum.name)))
        )

    # define training data and labels
    input_data = []
    output_data = []

    for enum, glob_elem in sample_images:
        for i in glob_elem:
            input_data.append(_calc_hist_from_file(i))
            output_data.append(enum.name)
    return input_data, output_data


def _load_classifier(filename: str) -> Optional[MLPClassifier]:
    if not os.path.isfile(filename):
        return None
    return load(filename)


def _train_classifier(input_data, output_data, filename: str = None):
    # instantiate classifier
    # Multi-layer Perceptron
    clf = MLPClassifier(solver="lbfgs")

    # split samples into training and test data
    x_train, x_test, y_train, y_test = train_test_split(input_data, output_data, test_size=.2)

    # train and score classifier
    clf.fit(x_train, y_train)
    score = int(clf.score(x_test, y_test) * 100)

    if filename is not None:
        dump(clf, filename)

    return clf, score


def _detect_circles(image):
    global CHIP_MIN_RADIUS, CHIP_MAX_RADIUS, CHIP_MIN_DISTANCE

    # blur the image using Gaussian blurring, where pixels closer to the center
    # contribute more "weight" to the average, first argument is the source image,
    # second argument is kernel size, third one is sigma (0 for autodetect)
    # we use a 9x9 kernel and let OpenCV detect sigma
    blurred = cv2.GaussianBlur(image, (9, 9), 0)

    # circles: A vector that stores x, y, r for each detected circle.
    # src_gray: Input image (grayscale)
    # CV_HOUGH_GRADIENT: Defines the detection method.
    # dp = 2.2: The inverse ratio of resolution
    # min_dist = 100: Minimum distance between detected centers
    # param_1 = 200: Upper threshold for the internal Canny edge detector
    # param_2 = 100*: Threshold for center detection.
    # min_radius = 50: Minimum radius to be detected.
    # max_radius = 120: Maximum radius to be detected.
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=2.2, minDist=CHIP_MIN_DISTANCE,
                               param1=200, param2=100, minRadius=CHIP_MIN_RADIUS, maxRadius=CHIP_MAX_RADIUS)
    return circles


def _predict_chip(clf, roi) -> PokerChip:
    # calculate feature vector for region of interest
    hist = _calc_histogram(roi)

    # predict chip value
    s = clf.predict([hist])

    return PokerChip[s[0]]


def _predict_chips(src, clf, circles, dst=None) -> List[PokerChip]:
    if len(circles) == 0:
        return []

    predictions = []

    # convert coordinates and radii to integers
    circles = np.round(circles[0, :]).astype("int")

    # loop over coordinates and radii of the circles
    for (x, y, d) in circles:
        # extract region of interest
        roi = src[y - d:y + d, x - d:x + d]

        if roi.size == 0:
            continue

        roi = cv2.resize(roi, (128, 128))

        # try recognition of chip feature and add result to list
        prediction = _predict_chip(clf, roi)
        predictions.append(prediction)

        if prediction.name == PokerChip.unknown.name:
            continue

        # draw contour and results in the output image
        if dst is not None:
            cv2.circle(dst, (x, y), d, (0, 255, 0), 2)
            cv2.putText(dst, prediction.name, (x - 40, y - 40), cv2.FONT_HERSHEY_PLAIN,
                        1.5, (0, 0, 255), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(dst, str(prediction.value), (x - 40, y), cv2.FONT_HERSHEY_PLAIN,
                        1.5, (0, 0, 255), thickness=2, lineType=cv2.LINE_AA)

    return predictions
