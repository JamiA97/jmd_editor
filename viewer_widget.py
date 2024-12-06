from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from markdown import markdown
from mdx_math import MathExtension


class ViewerPage(QWebEnginePage):
    """
    Custom QWebEnginePage to handle link navigation.
    We'll override acceptNavigationRequest to catch link clicks.
    """
    def __init__(self, parent=None, on_link_clicked=None):
        super().__init__(parent)
        self.on_link_clicked = on_link_clicked

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        # If it's a user click on a link, handle it
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            if self.on_link_clicked:
                self.on_link_clicked(url.toString())
            return False  # We'll handle navigation manually
        return True


class ViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Toolbar with Back button
        self.toolbar = QToolBar(self)
        self.layout.addWidget(self.toolbar)

        self.back_action = QAction("Back", self)
        self.back_action.triggered.connect(self.go_back)
        self.back_action.setEnabled(False)
        self.toolbar.addAction(self.back_action)

        self.webview = QWebEngineView(self)
        self.layout.addWidget(self.webview)

        # Store current markdown and original HTML for "Back" functionality
        self.current_markdown = ""
        self.original_markdown = ""
        self.page = ViewerPage(on_link_clicked=self.open_link)
        self.webview.setPage(self.page)

    def update_content(self, markdown_text):
        self.current_markdown = markdown_text
        self.original_markdown = markdown_text
        self.back_action.setEnabled(False)

        # Convert Markdown to HTML (with math)
        html_content = markdown(
            markdown_text,
            extensions=[
                'extra',
                'codehilite',
                MathExtension()
            ]
        )

        # KaTeX integration
        katex_script = """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css">
        <script defer src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js"></script>
        <script defer src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                renderMathInElement(document.body, {
                    delimiters: [
                        {left: "$$", right: "$$", display: true},  // Block math
                        {left: "\\[", right: "\\]", display: true},  // Alternative block math
                        {left: "$", right: "$", display: false},  // Inline math
                        {left: "\\(", right: "\\)", display: false}  // Alternative inline math
                    ]
                });
            });
        </script>
        """


        style = """
        <style>
            body {
                font-family: 'Arial';
                font-size: 14px;
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
        
        # Save the HTML to debug file
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(final_html)

        # Load the HTML into the QWebEngineView
        self.webview.setHtml(final_html, QUrl("about:blank"))

    def open_link(self, url):
        # Called when a link is clicked
        print(f"Link clicked: {url}")
        if url.startswith("http://") or url.startswith("https://"):
            # Open in default browser
            from PyQt5.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl(url))
            self.back_action.setEnabled(True)
        elif url.startswith("file://"):
            # Local file - if markdown, load it
            local_path = url[7:]
            if local_path.endswith(".md"):
                try:
                    with open(local_path, "r", encoding="utf-8") as f:
                        markdown_content = f.read()
                    self.current_markdown = markdown_content
                    self.back_action.setEnabled(True)
                    self.update_content(markdown_content)
                except Exception as e:
                    print(f"Error loading local Markdown file: {e}")
            else:
                print(f"Unsupported file type: {local_path}")
        else:
            # Other links - just try loading them
            self.webview.load(QUrl(url))
            self.back_action.setEnabled(True)

    def go_back(self):
        # Restore the original markdown
        if self.original_markdown:
            self.update_content(self.original_markdown)
            self.back_action.setEnabled(False)
