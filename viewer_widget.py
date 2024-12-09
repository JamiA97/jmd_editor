from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtCore import Qt
from markdown import markdown
from mdx_math import MathExtension
import os

class ViewerWidget(QWidget):
    file_selected_for_editor = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.webview = QWebEngineView(self)
        self.layout.addWidget(self.webview)

        self.current_markdown = ""
        self.current_file_path = None  # Keep track of the current file being rendered

        self.webview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.webview.customContextMenuRequested.connect(self.show_context_menu)

        self.page = QWebEnginePage(self)
        self.page.acceptNavigationRequest = self.intercept_link_navigation
        self.webview.setPage(self.page)

    def intercept_link_navigation(self, url, nav_type, is_main_frame):
        """
        Intercept link clicks in the preview window to handle .md files.
        """
        print(f"Intercepted URL: {url.toString()}")
        local_path = url.toLocalFile()
        print(f"Local path derived: {local_path}")

        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            if local_path.endswith(".md"):
                print(f"Markdown file detected: {local_path}")
                self.load_markdown_file(local_path)
                return False  # Prevent default navigation
            else:
                print(f"Non-Markdown link clicked: {url.toString()}")
        return True

    def load_markdown_file(self, file_path):
        """
        Load and render a Markdown file in the preview window.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Loaded content from {file_path}")
            self.current_file_path = file_path
            self.update_content(content, os.path.dirname(file_path))
        except Exception as e:
            print(f"Error loading Markdown file: {e}")

    def update_content(self, markdown_text, base_url):
        """
        Convert Markdown to HTML and display it in the web view.
        """
        self.current_markdown = markdown_text
        html_content = markdown(
            markdown_text,
            extensions=[
                'extra',
                'codehilite',
                MathExtension()
            ]
        )

        # KaTeX setup
        katex_path = os.path.abspath("assets/katex")
        katex_script = f"""
        <link rel="stylesheet" href="file:///{katex_path}/katex.min.css">
        <script defer src="file:///{katex_path}/katex.min.js"></script>
        <script defer src="file:///{katex_path}/contrib/auto-render.min.js"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                renderMathInElement(document.body, {{
                    delimiters: [
                        {{left: "$$", right: "$$", display: true}},
                        {{left: "\\\\[", right: "\\\\]", display: true}},
                        {{left: "$", right: "$", display: false}},
                        {{left: "\\\\(", right: "\\\\)", display: false}}
                    ]
                }});
            }});
        </script>
        """

        style = """
        <style>
            body {
                font-family: 'Raleway', sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: #222;
                background-color: #FFFFEE;
            }
        </style>
        """

        final_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        {katex_script}
        {style}
        </head>
        <body>{html_content}</body>
        </html>
        """

        # Debugging: Write final HTML to a file
        with open("debug_render.html", "w", encoding="utf-8") as file:
            file.write(final_html)

        print(f"Generated HTML for preview:\n{final_html}")

        self.webview.setHtml(final_html, QUrl.fromLocalFile(base_url + '/'))

    def show_context_menu(self, position):
        """
        Show a context menu in the preview window for additional actions.
        """
        menu = QMenu(self)
        open_in_editor_action = menu.addAction("Open in Editor")
        action = menu.exec_(self.webview.mapToGlobal(position))

        if action == open_in_editor_action and self.current_file_path:
            print(f"Opening {self.current_file_path} in the editor.")
            self.file_selected_for_editor.emit(self.current_file_path)
