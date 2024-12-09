from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import QUrl
from markdown import markdown
from mdx_math import MathExtension
import os

class ViewerPage(QWebEnginePage):
    def __init__(self, parent=None, on_link_clicked=None):
        super().__init__(parent)
        self.on_link_clicked = on_link_clicked

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        print(f"JS Console: {message} (source: {source_id}, line: {line_number})")

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            if self.on_link_clicked:
                self.on_link_clicked(url.toString())
            return False
        return True

class ViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.webview = QWebEngineView(self)
        self.layout.addWidget(self.webview)

        # Set attributes directly on QWebEngineSettings
        self.webview.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.webview.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        self.current_markdown = ""
        self.original_markdown = ""
        self.page = ViewerPage(on_link_clicked=self.open_link)
        self.webview.setPage(self.page)

    def update_content(self, markdown_text, base_url):
        """
        Converts Markdown to HTML and displays it in the web view.
        """
        self.current_markdown = markdown_text
        self.original_markdown = markdown_text

        # Convert Markdown to HTML
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

        print(f"Generated HTML:\n{final_html}")

        self.webview.setHtml(final_html, QUrl.fromLocalFile(base_url + '/'))

    def open_link(self, url):
        """
        Handles clicks on links in the preview. Renders markdown files as Markdown, handles other files normally.
        """
        print(f"Link clicked: {url}")
        if url.startswith("http://") or url.startswith("https://"):
            # Open external links in the system's default browser
            from PyQt5.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl(url))
        elif url.startswith("file://"):
            # Handle local files
            local_path = url[7:]  # Strip 'file://' prefix
            if local_path.endswith(".md"):
                # If it's a Markdown file, render it
                try:
                    with open(local_path, "r", encoding="utf-8") as f:
                        markdown_content = f.read()
                    # Update the content and set the correct base URL
                    self.update_content(markdown_content, os.path.dirname(local_path))
                except Exception as e:
                    print(f"Error loading Markdown file: {e}")
            else:
                # For non-Markdown files, attempt to load in the webview
                self.webview.load(QUrl(url))
        else:
            # Handle other URLs (e.g., relative paths)
            self.webview.load(QUrl(url))
