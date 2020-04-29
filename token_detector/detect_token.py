import argparse
import glob

import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from token_detector.token_color_enum import TokenColor
from token_detector.token_value_enum import TokenValue


def parse_arguments():
    # construct argument parser and parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to image")
    return vars(ap.parse_args())


# resize image while retaining aspect ratio
def resize_image(img, width):
    d = float(width) / img.shape[1]
    dim = (width, int(round(img.shape[0] * d)))
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


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


def create_value_training_data_sets():
    # locate sample image files
    sample_images = []
    for enum in TokenValue:
        sample_images.append(
            (enum, glob.glob("sample_images/tokens/values/{}/*".format(enum.name)))
        )

    # define training data and labels
    input_data = []
    output_data = []

    for enum, glob_elem in sample_images:
        for i in glob_elem:
            input_data.append(calc_hist_from_file(i))
            output_data.append(enum.name)
    return input_data, output_data


def create_color_training_data_sets():
    # locate sample image files
    sample_images = []
    for enum in TokenColor:
        sample_images.append(
            (enum, glob.glob("sample_images/tokens/colors/{}/*".format(enum.name).lower()))
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


def predict_value(clf, roi):
    # calculate feature vector for region of interest
    hist = calc_histogram(roi)

    # predict token value
    s = clf.predict([hist])

    return TokenValue[s[0]]


def predict_color(clf, roi):
    # calculate feature vector for region of interest
    hist = calc_histogram(roi)

    # predict token color
    s = clf.predict([hist])

    return TokenColor[s[0]]


def predict_token_values(src, dest, clf, circles):
    predictions = []
    count = 0
    if circles is not None:
        # convert coordinates and radii to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over coordinates and radii of the circles
        for (x, y, d) in circles:
            count += 1

            # extract region of interest
            roi = src[y - d:y + d, x - d:x + d]

            # try recognition of token feature and add result to list
            prediction = predict_value(clf, roi).name
            predictions.append(prediction)

            # draw contour and results in the output image
            cv2.circle(dest, (x, y), d, (0, 255, 0), 2)
            cv2.putText(dest, prediction, (x - 40, y), cv2.FONT_HERSHEY_PLAIN,
                        1.5, (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    return count


def main():
    args = parse_arguments()
    image = cv2.imread(args["image"])
    image = resize_image(image, 1024)

    # create a copy of the image to display results
    output = image.copy()

    # convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # improve contrast accounting for differences in lighting conditions:
    # create a CLAHE object to apply contrast limiting adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    input_data, output_data = create_value_training_data_sets()
    clf, score = train_classifier(input_data, output_data)

    circles = detect_circles(gray)

    token_count = predict_token_values(image, output, clf, circles)

    # resize input and output images
    image = resize_image(image, 768)
    output = resize_image(output, 768)

    # write summary on output image
    cv2.putText(output, "Tokens detected: {}".format(token_count),
                (5, output.shape[0] - 24), cv2.FONT_HERSHEY_PLAIN,
                1.0, (0, 0, 255), lineType=cv2.LINE_AA)
    cv2.putText(output, "Classifier mean accuracy: {}%".format(score),
                (5, output.shape[0] - 8), cv2.FONT_HERSHEY_PLAIN,
                1.0, (0, 0, 255), lineType=cv2.LINE_AA)

    # show output and wait for key to terminate program
    cv2.imshow("Output", np.hstack([image, output]))
    cv2.waitKey()


if __name__ == '__main__':
    main()
