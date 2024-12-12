from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction, QListWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from markdown import markdown
from mdx_math import MathExtension
import os
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
import re
from PIL import Image  # For aspect ratio calculation


class ImageResizerPostprocessor(Postprocessor):
    def run(self, text):
        def replace_image(match):
            src, alt, params = match.group(1), match.group(2), match.group(3)
            styles = []
            if "width" in params:
                width = re.search(r'width=(\d+)', params).group(1)
                styles.append(f"width:{width}px")
            if "height" in params:
                height = re.search(r'height=(\d+)', params).group(1)
                styles.append(f"height:{height}px")
            style_attr = f'style="{";".join(styles)}"' if styles else ""
            return f'<img src="{src}" alt="{alt}" {style_attr}>'

        return re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\){([^}]+)}',
            replace_image,
            text,
        )


class ImageResizerExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(ImageResizerPostprocessor(md), 'image_resizer', 175)


def calculate_aspect_ratio(image_path, width=None, height=None):
    """
    Helper function to calculate the aspect ratio of an image.
    """
    img = Image.open(image_path)
    original_width, original_height = img.size
    if width and not height:
        height = int((width / original_width) * original_height)
    elif height and not width:
        width = int((height / original_height) * original_width)
    return width, height


class ViewerWidget(QWidget):
    file_selected_for_editor = pyqtSignal(str)

    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path
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

        # Set webview settings
        self.webview.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.webview.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        # History stacks
        self.history_back = []
        self.history_forward = []

    def intercept_link_navigation(self, url, nav_type, is_main_frame):
        local_path = url.toLocalFile()
        #print(f"[DEBUG] Intercepted navigation to: {url.toString()}")
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            if url.toString().startswith(("http://", "https://")):
                from PyQt5.QtGui import QDesktopServices
                QDesktopServices.openUrl(url)
                print(f"[DEBUG] Opened external link in browser: {url.toString()}")
                return False  # Prevent default navigation
            elif local_path.endswith(".md"):
                self.navigate_to_file(local_path)
                print(f"[DEBUG] Navigating to Markdown file: {local_path}")
                return False  # Prevent default navigation
        return True

    def navigate_to_file(self, file_path):
        if self.current_file_path:
            if not self.history_back or self.history_back[-1] != self.current_file_path:
                self.history_back.append(self.current_file_path)
                print(f"[DEBUG] Added to Back History: {self.current_file_path}")
                print(f"[DEBUG] Current Back Stack: {self.history_back}")
        else:
            print(f"[DEBUG] First navigation to: {file_path}")

        self.history_forward.clear()
        print(f"[DEBUG] Cleared Forward Stack: {self.history_forward}")

        self.load_markdown_file(file_path)

    def load_markdown_file(self, file_path, search_term=None):
        """
        Load and render a Markdown file in the preview window, optionally highlighting search matches.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.current_file_path = file_path
            self.update_content(content, os.path.dirname(file_path), search_term)
            print(f"[DEBUG] Loaded and rendered: {file_path}")
        except Exception as e:
            print(f"[DEBUG] Error loading Markdown file: {e}")

    def highlight_matches(self, markdown_text, search_term):
        """
        Highlight search term matches in the Markdown content.
        """
        if not search_term:
            return markdown_text

        # Escape the search term for regex
        escaped_term = re.escape(search_term)
        highlighted_text = re.sub(
            rf"({escaped_term})",
            r'<span style="background-color: yellow; color: black;">\1</span>',
            markdown_text,
            flags=re.IGNORECASE
        )
        return highlighted_text

    def update_content(self, markdown_text, base_url, search_term=None):
        """
        Convert Markdown to HTML and display it in the web view, highlighting search matches.
        """
        if search_term:
            markdown_text = self.highlight_matches(markdown_text, search_term)

        # Process Markdown with extensions
        html_content = markdown(
            markdown_text,
            extensions=[
                'extra',
                'codehilite',
                MathExtension(),
                ImageResizerExtension()  # Add custom extension
            ]
        )

        # KaTeX setup
        katex_path = os.path.abspath(os.path.join(self.base_path, "assets", "katex"))
        katex_css = QUrl.fromLocalFile(os.path.join(katex_path, "katex.min.css")).toString()
        katex_js = QUrl.fromLocalFile(os.path.join(katex_path, "katex.min.js")).toString()
        auto_render_js = QUrl.fromLocalFile(os.path.join(katex_path, "contrib", "auto-render.min.js")).toString()

        katex_script = f"""
        <link rel="stylesheet" href="{katex_css}">
        <script defer src="{katex_js}"></script>
        <script defer src="{auto_render_js}"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                renderMathInElement(document.body, {{
                    delimiters: [
                        {{left: "$$", right: "$$", display: true}},
                        {{left: "\\[", right: "\\]", display: true}},
                        {{left: "$", right: "$", display: false}},
                        {{left: "\\(", right: "\\)", display: false}}
                    ]
                }});
            }});
        </script>
        """

        # Add CSS styles
        style = f"""
        <style>
            @font-face {{
                font-family: 'Raleway';
                src: url('file://{os.path.join(self.base_path, "assets", "Raleway", "static", "Raleway-Regular.ttf")}');
                font-weight: 400;
            }}
            @font-face {{
                font-family: 'Raleway';
                src: url('file://{os.path.join(self.base_path, "assets", "Raleway", "static", "Raleway-Bold.ttf")}');
                font-weight: 700;
            }}
            body {{
                font-family: 'Raleway', sans-serif;
                font-size: 18px;
                font-weight: 400;
                color: #222;
                background-color: #FFFFEE;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
            span[style*="background-color: yellow"] {{
                font-weight: bold;
            }}
        </style>
        """

        # Combine everything into the final HTML
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

        base_qurl = QUrl.fromLocalFile(base_url + os.sep)
        self.webview.setHtml(final_html, base_qurl)
        print("[DEBUG] HTML content updated.")

    def navigate_back(self):
        if self.history_back:
            last_file = self.history_back.pop()
            self.history_forward.append(self.current_file_path)
            self.load_markdown_file(last_file)

    def navigate_forward(self):
        if self.history_forward:
            next_file = self.history_forward.pop()
            self.history_back.append(self.current_file_path)
            self.load_markdown_file(next_file)

    def show_context_menu(self, position):
        menu = QMenu(self)
        open_in_editor_action = menu.addAction("Open in Editor")
        back_action = menu.addAction("Back")
        forward_action = menu.addAction("Forward")

        back_action.setEnabled(len(self.history_back) > 0)
        forward_action.setEnabled(len(self.history_forward) > 0)

        action = menu.exec_(self.webview.mapToGlobal(position))

        if action == open_in_editor_action and self.current_file_path:
            self.file_selected_for_editor.emit(self.current_file_path)
        elif action == back_action:
            self.navigate_back()
        elif action == forward_action:
            self.navigate_forward()
