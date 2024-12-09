from PyQt5.QtWidgets import QFileDialog, QMessageBox


class FileManager:
    def __init__(self, editor_widget):
        self.editor_widget = editor_widget
        self.current_file = None

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open File", "", "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor_widget.set_content(content)
                self.current_file = file_path
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Unable to open file: {e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor_widget.get_content())
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Unable to save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save File", "", "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.editor_widget.get_content())
                self.current_file = file_path
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Unable to save file: {e}")

    def close_file(self):
        self.editor_widget.set_content("")
        self.current_file = None
