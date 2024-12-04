import tkinter as tk
from editor_frame import EditorFrame
from viewer_frame import ViewerFrame
from file_manager import FileManager


class MarkdownEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Markdown Editor")
        self.root.geometry("800x600")

        # Create a PanedWindow to hold the editor and viewer frames
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Initialize editor and viewer frames
        self.editor_frame = EditorFrame(self.paned_window, self.update_viewer)
        self.viewer_frame = ViewerFrame(self.paned_window)

        # Add frames to the PanedWindow
        self.paned_window.add(self.editor_frame, stretch="always")
        self.paned_window.add(self.viewer_frame, stretch="always")

        # Initialize file manager
        self.file_manager = FileManager(self.editor_frame)

        # Menu setup
        self.setup_menu()

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu = tk.Menu(menu_bar, tearoff=0)

        # File menu options
        file_menu.add_command(label="Open", command=self.file_manager.open_file)
        file_menu.add_command(label="Save", command=self.file_manager.save_file)
        file_menu.add_command(label="Save As", command=self.file_manager.save_file_as)
        file_menu.add_command(label="Close", command=self.file_manager.close_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu options
        edit_menu.add_command(label="Undo", command=self.editor_frame.undo)
        edit_menu.add_command(label="Redo", command=self.editor_frame.redo)

        # Add menus to menu bar
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        self.root.config(menu=menu_bar)

    def update_viewer(self):
        content = self.editor_frame.get_content()
        self.viewer_frame.update_content(content)


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownEditorApp(root)
    root.mainloop()
