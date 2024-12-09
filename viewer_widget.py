from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from markdown import markdown
from mdx_math import MathExtension
import os
from PyQt5.QtWebEngineWidgets import QWebEngineSettings


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


    def update_content(self, markdown_text, base_url):
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

        self.webview.setHtml(final_html, QUrl.fromLocalFile(base_url + '/'))
