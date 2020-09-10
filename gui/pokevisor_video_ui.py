import os
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog

import cv2

from game_supervisor import game_image_processing, game_supervision


class PokeVisorVideoUi(Tk):
    def __init__(self):
        super().__init__(None)
        self.title('PokeVisor')

        video_label = ttk.LabelFrame(self, text="Video to load")

        self._video_text = StringVar()
        self._video_text.set(os.getcwd())
        video_input = ttk.Entry(video_label, width=60, textvariable=self._video_text)
        video_input.pack(side=LEFT, padx=5, pady=5)

        browse_video_button = ttk.Button(video_label, text="Browse", command=self._browse_videos)
        browse_video_button.pack(side=RIGHT, padx=5, pady=5)

        video_label.pack(padx=5, pady=5)

        classifier_label = ttk.LabelFrame(self, text="Chip classifier")

        self._classifier_text = StringVar()
        self._classifier_text.set(os.getcwd())
        classifier_input = ttk.Entry(classifier_label, width=60, textvariable=self._classifier_text)
        classifier_input.pack(side=LEFT, padx=5, pady=5)

        browse_classifier_button = ttk.Button(classifier_label, text="Browse", command=self._browse_classifiers)
        browse_classifier_button.pack(side=RIGHT, padx=5, pady=5)

        classifier_label.pack(padx=5, pady=5)

        chip_detection_label = ttk.LabelFrame(self, text="Chip detection")
        self._toggle_button = ttk.Button(chip_detection_label, text="On", command=self._toggle_chip_detection)
        self._toggle_button.pack(padx=5, pady=5)
        chip_detection_label.pack(padx=5, pady=5)

        start_button = ttk.Button(self, text="Start", command=self._start)
        start_button.pack(padx=5, pady=5)

    def _browse_classifiers(self):
        classifier_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select classifier",
                                                     filetypes=(("joblib files", "*.joblib"),))
        self._classifier_text.set(classifier_path)

    def _browse_videos(self):
        video_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select video file")
        self._video_text.set(video_path)

    def _toggle_chip_detection(self):
        button_text: str = self._toggle_button.config("text")[-1]
        if button_text.lower() == "on":
            self._toggle_button.config(text="Off")
        else:
            self._toggle_button.config(text="On")

    def _start(self):
        video_path = self._video_text.get()
        classifier_path = self._classifier_text.get()
        detect_chips = self._toggle_button.config("text")[-1].lower() == "on"

        cap = cv2.VideoCapture(video_path)

        _, frame = cap.read()

        game_image_processing.setup(frame, classifier_path=classifier_path, detect_chips=detect_chips)

        self.destroy()
        game_supervision.supervise_video(cap)


def main():
    status_ui = PokeVisorVideoUi()
    while True:
        status_ui.update()


if __name__ == "__main__":
    main()
