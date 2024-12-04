# file_manager.py
from tkinter import filedialog, messagebox

class FileManager:
    def __init__(self, editor_frame):
        self.editor_frame = editor_frame
        self.current_file = None

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                self.editor_frame.set_content(content)
                self.current_file = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Unable to open file: {e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w") as file:
                    file.write(self.editor_frame.get_content())
            except Exception as e:
                messagebox.showerror("Error", f"Unable to save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "w") as file:
                    file.write(self.editor_frame.get_content())
                self.current_file = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Unable to save file: {e}")

    def close_file(self):
        self.editor_frame.set_content("")
        self.current_file = None

