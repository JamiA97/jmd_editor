from PyQt5.QtWidgets import QFileDialog, QMessageBox
import datetime
import uuid



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


    def create_new_file(self):
        # Generate timestamp and UUID for the file
        now = datetime.datetime.now()
        timestamp = now.strftime("%d%m%y_%H%M%S")  # File-safe timestamp
        nice_date = now.strftime("%d %B %Y")       # Human-readable date
        nice_time = now.strftime("%H:%M:%S")       # Human-readable time
        uuid_string = timestamp                    # Use the timestamp as UUID

        # Template content
        template_content = (
            f"### Date: {nice_date}\n"
            f"### Time: {nice_time}\n"
            f"### UUID: {uuid_string}\n\n"
            f"# Title:\n\n"
            f"**Tags**\n\n"
            f"### Body:\n"
        )

        # Default filename
        default_name = f"{timestamp}.md"

        # Show a "Save As" dialog with the default name
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Create New Markdown File", default_name, "Markdown Files (*.md)"
        )

        if file_path:
            # Ensure the file has a .md extension
            if not file_path.endswith(".md"):
                file_path += ".md"
            try:
                # Create the file with the template content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(template_content)
                
                self.current_file = file_path
                self.editor_widget.set_content(template_content)  # Load template into editor
                
                QMessageBox.information(None, "File Created", f"New file created: {file_path}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Unable to create file: {e}")
