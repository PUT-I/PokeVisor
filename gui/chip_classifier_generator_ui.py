import os
import tkinter.messagebox as tk_msg
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog

from logic.chip_detector import chip_detection


class ChipClassifierGeneratorUi(Tk):
    def __init__(self):
        super().__init__(None)
        self.title("Chip classifier generator")

        samples_label = ttk.LabelFrame(self, text="Sample images")

        self._samples_text = StringVar()
        self._samples_text.set(os.getcwd())
        samples_input = ttk.Entry(samples_label, width=60, textvariable=self._samples_text)
        samples_input.pack(side=LEFT, padx=5, pady=5)

        browse_button = ttk.Button(samples_label, text="Browse", command=self._browse_files)
        browse_button.pack(side=RIGHT, padx=5, pady=5)

        samples_label.pack(padx=5, pady=5)

        train_label = ttk.LabelFrame(self, text="Classifier training")

        self._out_text = StringVar()
        self._out_text.set("classifier.joblib")
        out_input = ttk.Entry(train_label, width=60, textvariable=self._out_text)
        out_input.pack(side=LEFT, padx=5, pady=5)
        out_button = ttk.Button(train_label, text="Train", command=self._train_classifier)
        out_button.pack(side=RIGHT, padx=5, pady=5)

        train_label.pack(padx=5, pady=5)

        self.resizable(False, False)

    def _browse_files(self):
        samples_dir = filedialog.askdirectory(initialdir=os.getcwd(), title="Select sample images directory")
        self._samples_text.set(samples_dir)

    def _train_classifier(self):
        sample_images_path: str = self._samples_text.get()
        output_filename: str = self._out_text.get()

        try:
            chip_detection.generate_classifier(sample_images_path, output_filename)
            tk_msg.showinfo("Training finished",
                            "Classifier has been trained and saved to: {}.".format(output_filename))
        except FileNotFoundError:
            tk_msg.showerror("Samples not found", "Samples not found in: {}.".format(sample_images_path))


if __name__ == "__main__":
    classifier_generator = ChipClassifierGeneratorUi()
    classifier_generator.mainloop()
