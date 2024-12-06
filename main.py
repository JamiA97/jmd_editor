# main.py

import tkinter as tk
from tkinter import font
from editor_frame import EditorFrame
from viewer_frame import ViewerFrame
from file_manager import FileManager


class MarkdownEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Markdown Editor")
        self.root.geometry("1000x700")  # Set initial window size

        # Load custom font
        font_path = "assets/Raleway/Raleway-VariableFont_wght.ttf"
        try:
            self.custom_font = font.Font(file=font_path, size=12)  # Create a tkinter font object
        except Exception as e:
            print(f"Error loading custom font: {e}")
            self.custom_font = font.Font(family="TkDefaultFont", size=12)  # Fallback to default font

        # Initialize a BooleanVar to track preview visibility
        self.preview_visible = tk.BooleanVar(value=True)

        # Create a PanedWindow to hold the editor and viewer frames
        self.paned_window = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Initialize editor and viewer frames
        self.editor_frame = EditorFrame(self.paned_window, self.update_viewer, self.custom_font)
        self.viewer_frame = ViewerFrame(self.paned_window)

        # Add frames to the PanedWindow
        self.paned_window.add(self.editor_frame, stretch="always")
        self.paned_window.add(self.viewer_frame, stretch="always")

        # Initialize file manager
        self.file_manager = FileManager(self.editor_frame)

        # Menu setup
        self.setup_menu()

    def setup_menu(self):
        """Set up the application menu."""
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu = tk.Menu(menu_bar, tearoff=0)  # View menu for toggling the preview

        # File menu options
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.file_manager.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.file_manager.save_file)
        file_menu.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=self.file_manager.save_file_as)
        file_menu.add_command(label="Close", command=self.file_manager.close_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu options
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.editor_frame.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.editor_frame.redo)

        # View menu options
        view_menu.add_checkbutton(
            label="Show Preview",
            variable=self.preview_visible,
            onvalue=True,
            offvalue=False,
            command=self.toggle_preview
        )

        # Add menus to menu bar
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)  # Add View menu
        self.root.config(menu=menu_bar)

        # Bind keyboard shortcuts
        self.bind_shortcuts()

    def bind_shortcuts(self):
        """Bind keyboard shortcuts for common actions."""
        self.root.bind("<Control-o>", lambda event: self.file_manager.open_file())
        self.root.bind("<Control-s>", lambda event: self.file_manager.save_file())
        self.root.bind("<Control-S>", lambda event: self.file_manager.save_file_as())
        self.root.bind("<Control-z>", lambda event: self.editor_frame.undo())
        self.root.bind("<Control-y>", lambda event: self.editor_frame.redo())

    def toggle_preview(self):
        """Show or hide the preview pane based on the 'Show Preview' toggle."""
        if self.preview_visible.get():
            self.paned_window.add(self.viewer_frame, stretch="always")
            print("Preview pane shown.")
        else:
            self.paned_window.forget(self.viewer_frame)
            print("Preview pane hidden.")

    def update_viewer(self):
        """Update the viewer with the latest content from the editor."""
        content = self.editor_frame.get_content()
        self.viewer_frame.update_content(content)


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownEditorApp(root)
    root.mainloop()
