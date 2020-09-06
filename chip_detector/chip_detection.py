import glob

import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from chip_detector.classes.poker_chip_enum import PokerChip


def calc_histogram(hsv_img):
    # hsv_img = cv2.resize(hsv_img, (128, 128))

    # create mask
    m = np.zeros(hsv_img.shape[:2], dtype="uint8")
    (w, h) = (int(hsv_img.shape[1] / 2), int(hsv_img.shape[0] / 2))
    m = cv2.circle(m, (w, h), 60, 255, -1)

    # calcHist expects a list of images, color channels, mask, bins, ranges
    h = cv2.calcHist([hsv_img], [0, 1], m, [180, 255], [0, 180, 0, 255])

    # return normalized "flattened" histogram
    return cv2.normalize(h, h).flatten()


def calc_hist_from_file(file):
    img = cv2.imread(file)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return calc_histogram(img)


def create_color_training_data_sets():
    # locate sample image files
    sample_images = []
    for enum in PokerChip:
        sample_images.append(
            (enum, glob.glob("{}/{}/*".format("sample_images/", enum.name)))
        )

    # define training data and labels
    input_data = []
    output_data = []

    for enum, glob_elem in sample_images:
        for i in glob_elem:
            input_data.append(calc_hist_from_file(i))
            output_data.append(enum.name)
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
                               param1=200, param2=100, minRadius=20, maxRadius=120)
    return circles


def predict_color(clf, roi):
    # calculate feature vector for region of interest
    hist = calc_histogram(roi)

    # predict chip value
    s = clf.predict([hist])

    return PokerChip[s[0]]


def predict_chip_colors(src, clf, circles, dst=None):
    predictions = []
    if circles is not None:
        # convert coordinates and radii to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over coordinates and radii of the circles
        for (x, y, d) in circles:
            # extract region of interest
            roi = src[y - d:y + d, x - d:x + d]
            roi = cv2.resize(roi, (128, 128))

            # try recognition of chip feature and add result to list
            prediction = predict_color(clf, roi)
            predictions.append(prediction)

            if prediction.name == 'unknown':
                continue

            # draw contour and results in the output image
            if dst is not None:
                cv2.circle(dst, (x, y), d, (0, 255, 0), 2)
                cv2.putText(dst, prediction.name, (x - 40, y - 40), cv2.FONT_HERSHEY_PLAIN,
                            1.5, (0, 0, 255), thickness=2, lineType=cv2.LINE_AA)
                cv2.putText(dst, str(prediction.value), (x - 40, y), cv2.FONT_HERSHEY_PLAIN,
                            1.5, (0, 0, 255), thickness=2, lineType=cv2.LINE_AA)
    return predictions


def detect_chips(img, dst=None) -> list:
    # convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # improve contrast accounting for differences in lighting conditions:
    # create a CLAHE object to apply contrast limiting adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    input_color_data, output_color_data = create_color_training_data_sets()
    clf_color, _ = train_classifier(input_color_data, output_color_data)

    circles = detect_circles(gray)

    chip_colors = predict_chip_colors(hsv_img, clf_color, circles, dst=dst)

    return chip_colors
