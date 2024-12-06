# editor_frame.py
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Define color variables
BACKGROUND = "#FFFFEE"  # Light cream background
TEXT_COLOR = "#222"  # Dark text color



class EditorFrame(tk.Frame):
    def __init__(self, parent, update_viewer_callback, custom_font=None):
        super().__init__(parent)
        self.update_viewer_callback = update_viewer_callback

        # Editor area
        self.text_area = ScrolledText(self, wrap=tk.WORD, undo=True, bg=BACKGROUND, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        if custom_font:
            self.text_area.configure(font=custom_font)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.bind("<<Modified>>", self.on_text_change)

        # Debounce variables
        self._debounce_delay = 300  # milliseconds
        self._debounce_job = None

    def on_text_change(self, event=None):
        if self.text_area.edit_modified():
            if self._debounce_job is not None:
                self.after_cancel(self._debounce_job)
            self._debounce_job = self.after(self._debounce_delay, self.trigger_update)
            self.text_area.edit_modified(False)

    def trigger_update(self):
        self.update_viewer_callback()
        self._debounce_job = None

    def get_content(self):
        return self.text_area.get("1.0", tk.END)

    def set_content(self, content):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, content)

    def undo(self):
        self.text_area.edit_undo()

    def redo(self):
        self.text_area.edit_redo()
