import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction, QFileDialog,
                             QMessageBox, QSplitter, QWidget, QVBoxLayout, QCheckBox, QFrame)
from PyQt5.QtCore import Qt, QTimer
from editor_widget import EditorWidget
from viewer_widget import ViewerWidget
from file_manager import FileManager


class MarkdownEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Markdown Editor (PyQt5 Version)")
        self.resize(1000, 700)

        # Initialize central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a QSplitter for the editor and viewer
        self.splitter = QSplitter(Qt.Horizontal, self)
        layout.addWidget(self.splitter)

        # Initialize editor and viewer
        self.editor = EditorWidget(self.update_viewer)
        self.viewer = ViewerWidget()

        # Add them to the splitter
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.viewer)

        # File manager
        self.file_manager = FileManager(self.editor)

        # Initialize preview visibility state
        self.preview_visible = True

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
        close_act = QAction("Close", self, triggered=self.file_manager.close_file)
        exit_act = QAction("Exit", self, triggered=self.close)

        file_menu.addAction(open_act)
        file_menu.addAction(save_act)
        file_menu.addAction(save_as_act)
        file_menu.addAction(close_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

        # Edit menu actions
        undo_act = QAction("Undo", self, shortcut="Ctrl+Z", triggered=self.editor.undo)
        redo_act = QAction("Redo", self, shortcut="Ctrl+Y", triggered=self.editor.redo)
        edit_menu.addAction(undo_act)
        edit_menu.addAction(redo_act)

        # View menu actions (Show Preview)
        self.show_preview_act = QAction("Show Preview", self, checkable=True, checked=True)
        self.show_preview_act.triggered.connect(self.toggle_preview)
        view_menu.addAction(self.show_preview_act)

    def toggle_preview(self):
        if self.show_preview_act.isChecked():
            # Show preview
            if self.viewer not in [self.splitter.widget(i) for i in range(self.splitter.count())]:
                self.splitter.addWidget(self.viewer)
        else:
            # Hide preview
            idx = None
            for i in range(self.splitter.count()):
                if self.splitter.widget(i) is self.viewer:
                    idx = i
                    break
            if idx is not None:
                self.splitter.widget(idx).setParent(None)

    def update_viewer(self):
        content = self.editor.get_content()
        self.viewer.update_content(content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownEditorApp()
    window.show()
    sys.exit(app.exec_())
