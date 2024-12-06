from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QTimer

# This replaces the Tkinter ScrolledText editor.
# The logic remains similar: when text changes, we schedule an update of the preview.

class EditorWidget(QWidget):
    def __init__(self, update_viewer_callback):
        super().__init__()
        self.update_viewer_callback = update_viewer_callback
        self.layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)

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
