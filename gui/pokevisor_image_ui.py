import os
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog

import cv2

from game_supervisor import game_image_processing, game_supervision


class PokeVisorImageUi(Tk):
    def __init__(self):
        super().__init__(None)
        self.title('PokeVisor')

        image_label = ttk.LabelFrame(self, text="Images to load")

        self._image_text = StringVar()
        self._image_text.set(os.getcwd())
        image_input = ttk.Entry(image_label, width=60, textvariable=self._image_text)
        image_input.pack(side=LEFT, padx=5, pady=5)

        browse_image_button = ttk.Button(image_label, text="Browse", command=self._browse_videos)
        browse_image_button.pack(side=RIGHT, padx=5, pady=5)

        image_label.pack(padx=5, pady=5)

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
        image_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select images directory")
        self._image_text.set(image_path)

    def _toggle_chip_detection(self):
        button_text: str = self._toggle_button.config("text")[-1]
        if button_text.lower() == "on":
            self._toggle_button.config(text="Off")
        else:
            self._toggle_button.config(text="On")

    def _start(self):
        image_path = self._image_text.get()
        classifier_path = self._classifier_text.get()
        detect_chips = self._toggle_button.config("text")[-1].lower() == "on"

        images = []
        for root, _, files in os.walk(image_path, topdown=False):
            for file in files:
                image = cv2.imread("{}/{}".format(root, file))
                images.append(image)
        self.destroy()
        players = game_image_processing.setup(images[0], classifier_path=classifier_path, detect_chips=detect_chips)
        game_supervision.supervise_images(images, players)


def main():
    status_ui = PokeVisorImageUi()
    while True:
        try:
            status_ui.update()
        except TclError:
            break


if __name__ == "__main__":
    main()
