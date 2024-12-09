import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QAction, QFileDialog,
    QMessageBox, QSplitter, QWidget, QVBoxLayout, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont, QKeySequence
from editor_widget import EditorWidget
from viewer_widget import ViewerWidget
from file_manager import FileManager
from file_viewer_widget import FileViewerWidget


class MarkdownEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Markdown Editor (PyQt5 Version)")
        self.resize(1000, 700)

        # Determine the base path based on the script's location
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # Load the custom font
        font_path = os.path.join(self.base_path, "assets", "Raleway", "Raleway-VariableFont_wght.ttf")
        if QFontDatabase.addApplicationFont(font_path) == -1:
            print("Error: Failed to load the Raleway font.")
        else:
            print("Raleway font loaded successfully.")

        # Set the default font for the application
        raleway_font = QFont("Raleway", 12)
        raleway_font.setWeight(QFont.Bold)  # Set the font weight
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
        self.file_viewer.folder_changed.connect(self.set_working_folder)

        self.editor = EditorWidget(self.update_viewer)
        self.viewer = ViewerWidget(self.base_path)  # Pass base_path to ViewerWidget

        # Connect ViewerWidget's signal to the slot in main application
        self.viewer.file_selected_for_editor.connect(self.open_file_in_editor)
        print("[DEBUG] Connected ViewerWidget's 'file_selected_for_editor' signal to 'open_file_in_editor' slot.")

        # Add widgets to the splitter
        self.splitter.addWidget(self.file_viewer)
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.viewer)

        # Set initial sizes for the panes
        self.splitter.setSizes([200, 400, 400])

        # File manager
        self.file_manager = FileManager(self.editor)

        # Set up menu
        self.setup_menu()

        # Set an initial example Markdown content
        self.working_folder = os.getcwd()
        example_markdown = f"""
# Example Markdown

This is **bold text** and *italic text*.

Math: $E = mc^2$

Block math:
$
\\frac{{d}}{{dx}}f(x)=f'(x)
$

[Link to Markdown Guide](https://www.markdownguide.org)

![image](file:///{os.path.join(self.base_path, "images", "tux.png")})
"""
        self.editor.set_content(example_markdown)
        self.update_viewer()  # Initial render

        # Add shortcut for opening the current file in the editor
        shortcut_open_in_editor = QShortcut(QKeySequence("Ctrl+E"), self)
        shortcut_open_in_editor.activated.connect(self.open_current_viewed_file_in_editor)

        self.setup_navigation_shortcuts()

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
            print("[DEBUG] Editor shown.")
        else:
            self.editor.setParent(None)
            print("[DEBUG] Editor hidden.")

        if not self.show_editor_act.isChecked() and not self.show_preview_act.isChecked():
            self.show_preview_act.setChecked(True)
            self.toggle_preview()

    def toggle_preview(self):
        if self.show_preview_act.isChecked():
            self.splitter.addWidget(self.viewer)
            print("[DEBUG] Preview shown.")
        else:
            self.viewer.setParent(None)
            print("[DEBUG] Preview hidden.")

        if not self.show_editor_act.isChecked() and not self.show_preview_act.isChecked():
            self.show_editor_act.setChecked(True)
            self.toggle_editor()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder_path:
            self.working_folder = folder_path
            self.file_viewer.set_folder(folder_path)
            QMessageBox.information(self, "Working Folder Set", f"Working folder set to: {folder_path}")
            print(f"[DEBUG] Working folder set to: {folder_path}")

    def set_working_folder(self, folder_path):
        self.working_folder = folder_path
        QMessageBox.information(self, "Working Folder Set", f"Working folder set to: {folder_path}")
        print(f"[DEBUG] Working folder changed to: {folder_path}")

    def open_file_from_viewer(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.set_content(content)
            self.update_viewer()
            print(f"[DEBUG] Opened file from viewer: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to open file: {e}")
            print(f"[DEBUG] Error opening file from viewer: {e}")

    def open_file_in_editor(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.set_content(content)
            self.update_viewer()
            print(f"[DEBUG] Opened file in editor: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to open file: {e}")
            print(f"[DEBUG] Error opening file in editor: {e}")

    def open_current_viewed_file_in_editor(self):
        if hasattr(self.viewer, 'current_file_path') and self.viewer.current_file_path:
            self.open_file_in_editor(self.viewer.current_file_path)
            print("[DEBUG] Opened current viewed file in editor via shortcut.")
        else:
            QMessageBox.warning(self, "No File", "No file is currently loaded in the preview.")
            print("[DEBUG] No file loaded to open in editor via shortcut.")

    def update_viewer(self):
        content = self.editor.get_content()
        self.viewer.update_content(content, self.working_folder)
        print("[DEBUG] Viewer updated with new content.")

    def setup_navigation_shortcuts(self):
        back_shortcut = QShortcut(QKeySequence("Ctrl+Left"), self)
        back_shortcut.activated.connect(self.viewer.navigate_back)
        print("[DEBUG] Shortcut Ctrl+Left connected to navigate_back.")

        forward_shortcut = QShortcut(QKeySequence("Ctrl+Right"), self)
        forward_shortcut.activated.connect(self.viewer.navigate_forward)
        print("[DEBUG] Shortcut Ctrl+Right connected to navigate_forward.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownEditorApp()
    window.show()
    sys.exit(app.exec_())
