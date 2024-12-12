from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QTextEdit, QShortcut
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import QTimer
import os


class EnhancedTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def insert_file_link(self):
        """
        Opens a file dialog to select a file and inserts the relative path at the cursor position.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*.*)")
        if file_path:
            relative_path = os.path.relpath(file_path, os.getcwd())
            cursor = self.textCursor()
            cursor.insertText(relative_path)


class EditorWidget(QWidget):
    def __init__(self, update_viewer_callback):
        super().__init__()
        self.update_viewer_callback = update_viewer_callback
        self.layout = QVBoxLayout(self)
        self.text_edit = EnhancedTextEdit(self)  # Use EnhancedTextEdit
        self.layout.addWidget(self.text_edit)

        # Apply the Raleway font
        specific_font = QFont("Raleway", 14)
        self.text_edit.setFont(specific_font)

        # Set the background color to match the viewer
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFEE;
                color: #222;  /* Match the viewer text color */
                border: none;
                font-weight: 600; /* Match the viewer font weight */
                font-family: 'Raleway', sans-serif;
            }
        """)

        # Create the Ctrl+L shortcut
        self.file_link_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.file_link_shortcut.activated.connect(self.insert_file_link)

        # Debounce similar to Tkinter version
        self._debounce_delay = 300
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self.trigger_update)

        # Connect text change signal
        self.text_edit.textChanged.connect(self.on_text_change)

    def on_text_change(self):
        # When text changes, restart the debounce timer
        if self._debounce_timer.isActive():
            self._debounce_timer.stop()
        self._debounce_timer.start(self._debounce_delay)

    def trigger_update(self):
        self.update_viewer_callback()

    def get_content(self):
        return self.text_edit.toPlainText()

    def set_content(self, content):
        self.text_edit.setPlainText(content)

    def undo(self):
        self.text_edit.undo()

    def redo(self):
        self.text_edit.redo()

    def insert_file_link(self):
        """
        Trigger the file dialog to insert a file link.
        """
        self.text_edit.insert_file_link()
