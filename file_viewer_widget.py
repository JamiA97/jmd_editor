from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QMessageBox, QMenu
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QListWidgetItem
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

    # def show_context_menu(self, position):
    #     """
    #     Shows a context menu for additional folder actions.
    #     """
    #     menu = QMenu(self)
    #     set_working_folder_action = menu.addAction("Set as Working Folder")
    #     action = menu.exec_(self.file_list.mapToGlobal(position))

    #     if action == set_working_folder_action:
    #         selected_item = self.file_list.currentItem()
    #         if selected_item and selected_item.text().startswith("[Folder] "):
    #             folder_name = selected_item.text()[len("[Folder] "):]
    #             selected_folder = os.path.join(self.current_folder, folder_name)
    #             self.folder_changed.emit(selected_folder)

    def show_context_menu(self, position):
        """
        Shows a context menu for additional folder actions.
        """
        menu = QMenu(self)
        set_working_folder_action = menu.addAction("Set as Working Folder")
        refresh_action = menu.addAction("Refresh")  # Add Refresh option
        action = menu.exec_(self.file_list.mapToGlobal(position))

        if action == set_working_folder_action:
            selected_item = self.file_list.currentItem()
            if selected_item and selected_item.text().startswith("[Folder] "):
                folder_name = selected_item.text()[len("[Folder] "):]
                selected_folder = os.path.join(self.current_folder, folder_name)
                self.folder_changed.emit(selected_folder)
        elif action == refresh_action:
            self.refresh()  # Call the refresh method



    def refresh(self):
        """
        Refresh the file viewer to reflect the current folder's contents.
        """
        if self.current_folder:
            self.populate_file_list()
    

    def search_files(self, search_term):
        """
        Search for files and content matching the search term.
        """
        if not self.current_folder or not os.path.isdir(self.current_folder):
            QMessageBox.warning(self, "Invalid Workspace", "The current workspace folder is invalid or not set.")
            return

        results = []
        for root, _, files in os.walk(self.current_folder):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)

                    # Check filenames
                    if search_term.lower() in file.lower():
                        results.append((file_path, "Filename"))

                    # Check content
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        if search_term.lower() in content.lower():
                            results.append((file_path, "Content"))
                    except Exception as e:
                        QMessageBox.warning(self, "File Read Error", f"Error reading {file_path}: {e}")

        self.display_search_results(results)

    def display_search_results(self, results):
        """
        Display search results in the file viewer.
        """
        self.file_list.itemClicked.disconnect()  # Avoid duplicate connections
        self.file_list.clear()
        if not results:
            QMessageBox.information(self, "No Results", "No matches found.")
            return

        for file_path, match_type in results:
            display_text = f"{match_type}: {os.path.basename(file_path)}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.UserRole, file_path)  # Store file path in item data
            self.file_list.addItem(list_item)

        self.file_list.itemClicked.connect(self.open_search_result)

    def open_search_result(self, item):
        """
        Open the file clicked in the search results.
        """
        file_path = item.data(Qt.UserRole)
        self.file_selected.emit(file_path)