from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from markdown import markdown
from mdx_math import MathExtension
import os

class ViewerPage(QWebEnginePage):
    def __init__(self, parent=None, on_link_clicked=None):
        super().__init__(parent)
        self.on_link_clicked = on_link_clicked        

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

        self.current_markdown = ""
        self.original_markdown = ""
        self.page = ViewerPage(on_link_clicked=self.open_link)
        self.webview.setPage(self.page)

    def update_content(self, markdown_text):
        self.current_markdown = markdown_text
        self.original_markdown = markdown_text

        html_content = markdown(
            markdown_text,
            extensions=[
                'extra',
                'codehilite',
                MathExtension()
            ]
        )

        katex_script = """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css">
        <script defer src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js"></script>
        <script defer src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                renderMathInElement(document.body, {
                    delimiters: [
                        {left: "$$", right: "$$", display: true},
                        {left: "\\[", right: "\\]", display: true},
                        {left: "$", right: "$", display: false},
                        {left: "\\(", right: "\\)", display: false}
                    ]
                });
            });
        </script>
        """

        style = f"""
        <style>
            body {{
                font-family: 'Raleway', sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: #222;
                background-color: #FFFFEE;
            }}
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

        self.webview.setHtml(final_html, QUrl("about:blank"))

    def open_link(self, url):
        print(f"Link clicked: {url}")
        if url.startswith("http://") or url.startswith("https://"):
            from PyQt5.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl(url))
        elif url.startswith("file://"):
            local_path = url[7:]
            if local_path.endswith(".md"):
                try:
                    with open(local_path, "r", encoding="utf-8") as f:
                        markdown_content = f.read()
                    self.current_markdown = markdown_content
                    self.update_content(markdown_content)
                except Exception as e:
                    print(f"Error loading local Markdown file: {e}")
            else:
                print(f"Unsupported file type: {local_path}")
        else:
            self.webview.load(QUrl(url))

    def go_back(self):
        if self.original_markdown:
            self.update_content(self.original_markdown)
