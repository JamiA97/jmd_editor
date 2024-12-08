import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction, QFileDialog,
                             QMessageBox, QSplitter, QWidget, QVBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont
from editor_widget import EditorWidget
from viewer_widget import ViewerWidget
from file_manager import FileManager
from file_viewer_widget import FileViewerWidget


class MarkdownEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Markdown Editor (PyQt5 Version)")
        self.resize(1000, 700)

        # Load the custom font
        font_path = os.path.join("assets", "Raleway", "Raleway-VariableFont_wght.ttf")
        if QFontDatabase.addApplicationFont(font_path) == -1:
            print("Error: Failed to load the Raleway font.")
        else:
            print("Raleway font loaded successfully.")

        # Set the default font for the application
        raleway_font = QFont("Raleway", 12)
        QApplication.setFont(raleway_font)

        # Initialize central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a QSplitter for the panes
        self.splitter = QSplitter(Qt.Horizontal, self)
        layout.addWidget(self.splitter)

        # Initialize file viewer, editor, and viewer
        self.file_viewer = FileViewerWidget()
        self.file_viewer.file_selected.connect(self.open_file_from_viewer)

        self.editor = EditorWidget(self.update_viewer)
        self.viewer = ViewerWidget()

        # Add widgets to the splitter
        self.splitter.addWidget(self.file_viewer)
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.viewer)

        # Set initial sizes for the panes
        self.splitter.setSizes([200, 500, 300])

        # File manager
        self.file_manager = FileManager(self.editor)

        # Set up menu
        self.setup_menu()

        # Set an initial example Markdown content
        example_markdown = """
# Example Markdown

This is **bold text** and *italic text*.

Math: $E = mc^2$

Block math:
$$
\\frac{d}{dx}f(x)=f'(x)
$$

[Link to Markdown Guide](https://www.markdownguide.org)
"""
        self.editor.set_content(example_markdown)
        self.update_viewer()  # Initial render

    def setup_menu(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")

        # File menu actions
        open_act = QAction("Open", self, shortcut="Ctrl+O", triggered=self.file_manager.open_file)
        save_act = QAction("Save", self, shortcut="Ctrl+S", triggered=self.file_manager.save_file)
        save_as_act = QAction("Save As", self, shortcut="Ctrl+Shift+S", triggered=self.file_manager.save_file_as)
        select_folder_act = QAction("Select Folder", self, triggered=self.select_folder)
        exit_act = QAction("Exit", self, triggered=self.close)

        file_menu.addAction(open_act)
        file_menu.addAction(save_act)
        file_menu.addAction(save_as_act)
        file_menu.addAction(select_folder_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

        # Edit menu actions
        undo_act = QAction("Undo", self, shortcut="Ctrl+Z", triggered=self.editor.undo)
        redo_act = QAction("Redo", self, shortcut="Ctrl+Y", triggered=self.editor.redo)
        edit_menu.addAction(undo_act)
        edit_menu.addAction(redo_act)

        # View menu actions
        self.show_editor_act = QAction("Show Editor", self, checkable=True, checked=True)
        self.show_editor_act.triggered.connect(self.toggle_editor)
        view_menu.addAction(self.show_editor_act)

        self.show_preview_act = QAction("Show Preview", self, checkable=True, checked=True)
        self.show_preview_act.triggered.connect(self.toggle_preview)
        view_menu.addAction(self.show_preview_act)

    def toggle_editor(self):
        if self.show_editor_act.isChecked():
            self.splitter.addWidget(self.editor)
        else:
            self.editor.setParent(None)

        if not self.show_editor_act.isChecked() and not self.show_preview_act.isChecked():
            self.show_preview_act.setChecked(True)
            self.toggle_preview()

    def toggle_preview(self):
        if self.show_preview_act.isChecked():
            self.splitter.addWidget(self.viewer)
        else:
            self.viewer.setParent(None)

        if not self.show_editor_act.isChecked() and not self.show_preview_act.isChecked():
            self.show_editor_act.setChecked(True)
            self.toggle_editor()

    def select_folder(self):
        """
        Opens a dialog to select a folder for the file viewer.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder_path:
            self.file_viewer.set_folder(folder_path)

    def open_file_from_viewer(self, file_path):
        """
        Opens a file from the file viewer in the editor.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.set_content(content)
            self.update_viewer()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to open file: {e}")

    def update_viewer(self):
        content = self.editor.get_content()
        self.viewer.update_content(content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownEditorApp()
    window.show()
    sys.exit(app.exec_())
