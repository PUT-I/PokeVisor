import os
import tkinter as tk
import tkinter.messagebox as tk_msg
from tkinter import ttk, filedialog

from chip_detector import chip_detection


class ChipClassifierGenerator:
    def __init__(self):
        self._window = tk.Tk()
        self._window.title("Chip classifier generator")

        self._samples_label = ttk.LabelFrame(self._window, text="Sample images")

        self._samples_text = tk.StringVar()
        self._samples_text.set(os.getcwd())
        self._samples_input = ttk.Entry(self._samples_label, width=60, textvariable=self._samples_text)
        self._samples_input.pack(side=tk.LEFT, padx=5, pady=5)

        self._browse_button = ttk.Button(self._samples_label, text="Browse", command=self._browse_files)
        self._browse_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self._samples_label.pack(padx=5, pady=5)

        self._train_label = ttk.LabelFrame(self._window, text="Classifier training")

        self._out_text = tk.StringVar()
        self._out_text.set("classifier.joblib")
        self._out_input = ttk.Entry(self._train_label, width=60, textvariable=self._out_text)
        self._out_input.pack(side=tk.LEFT, padx=5, pady=5)
        self._out_button = ttk.Button(self._train_label, text="Train", command=self._train_classifier)
        self._out_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self._train_label.pack(padx=5, pady=5)

        self._window.resizable(False, False)

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
    window = ChipClassifierGenerator()
    tk.mainloop()
