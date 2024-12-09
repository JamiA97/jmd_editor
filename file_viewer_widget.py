from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QMessageBox, QMenu
from PyQt5.QtCore import pyqtSignal, Qt
import os

class FileViewerWidget(QWidget):
    # Signal to notify when a file or folder is selected
    file_selected = pyqtSignal(str)
    folder_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # List widget to display files and folders
        self.file_list = QListWidget(self)
        self.layout.addWidget(self.file_list)

        # Current folder being displayed
        self.current_folder = None

        # Connect item selection signal
        self.file_list.itemClicked.connect(self.on_item_clicked)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)

    def set_folder(self, folder_path):
        """
        Sets the folder and populates the list with its contents.
        """
        if not os.path.isdir(folder_path):
            QMessageBox.warning(self, "Invalid Folder", "The selected folder does not exist.")
            return

        self.current_folder = folder_path
        self.populate_file_list()

    def populate_file_list(self):
        """
        Populates the list with .md files and folders from the current folder.
        """
        self.file_list.clear()
        if not self.current_folder:
            return

        try:
            # Get all files and folders
            items = os.listdir(self.current_folder)
            if not items:
                QMessageBox.information(self, "No Files or Folders", "No files or folders found in the selected folder.")
                return

            # Separate folders and markdown files
            folders = [f for f in items if os.path.isdir(os.path.join(self.current_folder, f))]
            files = [f for f in items if f.endswith(".md") and os.path.isfile(os.path.join(self.current_folder, f))]

            # Add folders first (with a prefix or marker, if desired)
            self.file_list.addItems([f"[Folder] {folder}" for folder in sorted(folders)])
            
            # Add markdown files
            self.file_list.addItems(sorted(files))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list files and folders: {e}")

    def on_item_clicked(self, item):
        """
        Handles clicks on items in the file viewer.
        """
        text = item.text()
        if text.startswith("[Folder] "):
            # Navigate into the folder
            folder_name = text[len("[Folder] "):]
            new_folder = os.path.join(self.current_folder, folder_name)
            self.set_folder(new_folder)
        else:
            # Emit file_selected signal for files
            file_path = os.path.join(self.current_folder, text)
            self.file_selected.emit(file_path)

    def show_context_menu(self, position):
        """
        Shows a context menu for additional folder actions.
        """
        menu = QMenu(self)
        set_working_folder_action = menu.addAction("Set as Working Folder")
        action = menu.exec_(self.file_list.mapToGlobal(position))

        if action == set_working_folder_action:
            selected_item = self.file_list.currentItem()
            if selected_item and selected_item.text().startswith("[Folder] "):
                folder_name = selected_item.text()[len("[Folder] "):]
                selected_folder = os.path.join(self.current_folder, folder_name)
                self.folder_changed.emit(selected_folder)
