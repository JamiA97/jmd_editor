# editor_frame.py
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class EditorFrame(tk.Frame):
    def __init__(self, parent, update_viewer_callback):
        super().__init__(parent)
        self.update_viewer_callback = update_viewer_callback

        # Editor area
        self.text_area = ScrolledText(self, wrap=tk.WORD, undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.bind("<<Modified>>", self.on_text_change)

    def on_text_change(self, event=None):
        if self.text_area.edit_modified():
            self.update_viewer_callback()
            self.text_area.edit_modified(False)

    def get_content(self):
        return self.text_area.get("1.0", tk.END)

    def set_content(self, content):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, content)

    def undo(self):
        self.text_area.edit_undo()

    def redo(self):
        self.text_area.edit_redo()

