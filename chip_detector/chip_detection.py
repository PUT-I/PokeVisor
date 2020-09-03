import glob

import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from chip_detector.classes.chip_color_enum import ChipColor
from chip_detector.classes.chip_value_enum import ChipValue
from chip_detector.classes.poker_chip import PokerChip


def calc_histogram(img):
    # create mask
    m = np.zeros(img.shape[:2], dtype="uint8")
    (w, h) = (int(img.shape[1] / 2), int(img.shape[0] / 2))
    cv2.circle(m, (w, h), 60, 255, -1)

    # calcHist expects a list of images, color channels, mask, bins, ranges
    h = cv2.calcHist([img], [0, 1, 2], m, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    # return normalized "flattened" histogram
    return cv2.normalize(h, h).flatten()


def calc_hist_from_file(file):
    img = cv2.imread(file)
    return calc_histogram(img)


def _create_training_data_sets(images_path, enum_class):
    # locate sample image files
    sample_images = []
    for enum in enum_class:
        sample_images.append(
            (enum, glob.glob("{}/{}/*".format(images_path, enum.name)))
        )

    # define training data and labels
    input_data = []
    output_data = []

    for enum, glob_elem in sample_images:
        for i in glob_elem:
            input_data.append(calc_hist_from_file(i))
            output_data.append(enum.name)
    return input_data, output_data


def create_value_training_data_sets():
    input_data, output_data = _create_training_data_sets("sample_images/chips/values/", ChipValue)
    return input_data, output_data


def create_color_training_data_sets():
    input_data, output_data = _create_training_data_sets("sample_images/chips/colors/", ChipColor)
    return input_data, output_data


def train_classifier(input_data, output_data):
    # instantiate classifier
    # Multi-layer Perceptron
    # score: 0.974137931034
    clf = MLPClassifier(solver="lbfgs")

    # split samples into training and test data
    x_train, x_test, y_train, y_test = train_test_split(input_data, output_data, test_size=.2)

    # train and score classifier
    clf.fit(x_train, y_train)
    score = int(clf.score(x_test, y_test) * 100)
    print("Classifier mean accuracy: ", score)
    return clf, score


def detect_circles(image):
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
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=2.2, minDist=100,
                               param1=200, param2=100, minRadius=60, maxRadius=120)
    return circles


def _predict_feature(clf, roi, enum_class):
    # calculate feature vector for region of interest
    hist = calc_histogram(roi)

    # predict chip value
    s = clf.predict([hist])

    return enum_class[s[0]]


def predict_value(clf, roi):
    return _predict_feature(clf, roi, ChipValue)


def predict_color(clf, roi):
    return _predict_feature(clf, roi, ChipColor)


def _predict_chip_feature(src, clf, circles, predict_function, label_x_offset=40, label_y_offset=0, dst=None):
    predictions = []
    if circles is not None:
        # convert coordinates and radii to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over coordinates and radii of the circles
        for (x, y, d) in circles:
            # extract region of interest
            roi = src[y - d:y + d, x - d:x + d]

            # try recognition of chip feature and add result to list
            prediction = predict_function(clf, roi)
            predictions.append(prediction)

            # draw contour and results in the output image
            if dst is not None:
                cv2.circle(dst, (x, y), d, (0, 255, 0), 2)
                cv2.putText(dst, prediction.name, (x - label_x_offset, y - label_y_offset), cv2.FONT_HERSHEY_PLAIN,
                            1.5, (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    return predictions


def predict_chip_colors(src, clf, circles, dst=None):
    return _predict_chip_feature(src, clf, circles, predict_color, label_y_offset=10, dst=dst)


def predict_chip_values(src, clf, circles, dst=None):
    return _predict_chip_feature(src, clf, circles, predict_value, label_y_offset=40, dst=dst)


def detect_chips(image, dst=None) -> list:
    # convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # improve contrast accounting for differences in lighting conditions:
    # create a CLAHE object to apply contrast limiting adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    input_color_data, output_color_data = create_color_training_data_sets()
    clf_color, _ = train_classifier(input_color_data, output_color_data)

    input_value_data, output_value_data = create_value_training_data_sets()
    clf_value, _ = train_classifier(input_value_data, output_value_data)

    circles = detect_circles(gray)

    chip_colors = predict_chip_colors(image, clf_color, circles, dst=dst)
    chip_values = predict_chip_values(image, clf_value, circles, dst=dst)

    chips = []
    for color, value in zip(chip_colors, chip_values):
        chips.append(PokerChip(color, value))

    return chips
