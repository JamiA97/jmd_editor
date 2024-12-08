from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
import os

class FileViewerWidget(QWidget):
    # Signal to notify when a file is selected
    file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # List widget to display file names
        self.file_list = QListWidget(self)
        self.layout.addWidget(self.file_list)

        # Current folder being displayed
        self.current_folder = None

        # Connect item selection signal
        self.file_list.itemClicked.connect(self.on_file_selected)

    def set_folder(self, folder_path):
        """
        Sets the folder and populates the list with .md files.
        """
        if not os.path.isdir(folder_path):
            QMessageBox.warning(self, "Invalid Folder", "The selected folder does not exist.")
            return

        self.current_folder = folder_path
        self.populate_file_list()

    def populate_file_list(self):
        """
        Populates the list with .md files from the current folder.
        """
        self.file_list.clear()
        if not self.current_folder:
            return

        # Get all .md files
        try:
            files = [f for f in os.listdir(self.current_folder) if f.endswith(".md")]
            if not files:
                QMessageBox.information(self, "No Files", "No Markdown (.md) files found in the selected folder.")
            else:
                self.file_list.addItems(files)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list files: {e}")

    def on_file_selected(self, item):
        """
        Emits the file_selected signal when a file is clicked.
        """
        if self.current_folder:
            file_path = os.path.join(self.current_folder, item.text())
            self.file_selected.emit(file_path)
