from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from markdown import markdown
from mdx_math import MathExtension
import os


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
        """
        Intercept link clicks in the preview window to handle .md files.
        """
        local_path = url.toLocalFile()
        print(f"[DEBUG] Intercepted navigation to: {local_path}")
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            if local_path.endswith(".md"):
                self.navigate_to_file(local_path)
                print(f"[DEBUG] Navigating to Markdown file: {local_path}")
                return False  # Prevent default navigation
        return True

    def navigate_to_file(self, file_path):
        """
        Navigate to a new file, adding it to the history.
        """
        if self.current_file_path:
            # Add the current file to the back history only if it's not already the last entry
            if not self.history_back or self.history_back[-1] != self.current_file_path:
                self.history_back.append(self.current_file_path)
                print(f"[DEBUG] Added to Back History: {self.current_file_path}")
                print(f"[DEBUG] Current Back Stack: {self.history_back}")
        else:
            print(f"[DEBUG] First navigation to: {file_path}")

        # Clear the forward history when navigating to a new file
        self.history_forward.clear()
        print(f"[DEBUG] Cleared Forward Stack: {self.history_forward}")

        # Load the new file
        self.load_markdown_file(file_path)

    def load_markdown_file(self, file_path):
        """
        Load and render a Markdown file in the preview window.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.current_file_path = file_path
            self.update_content(content, os.path.dirname(file_path))
            print(f"[DEBUG] Loaded and rendered: {file_path}")
        except Exception as e:
            print(f"[DEBUG] Error loading Markdown file: {e}")

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

        # Convert base_url to a proper QUrl
        base_qurl = QUrl.fromLocalFile(base_url + os.sep)
        self.webview.setHtml(final_html, base_qurl)
        print(f"[DEBUG] HTML content set for base URL: {base_qurl.toString()}")

    def navigate_back(self):
        """
        Navigate to the previous file in history.
        """
        if self.history_back:
            last_file = self.history_back.pop()
            self.history_forward.append(self.current_file_path)
            print(f"[DEBUG] Popped from Back History: {last_file}")
            print(f"[DEBUG] Added to Forward Stack: {self.current_file_path}")
            self.load_markdown_file(last_file)
            print(f"[DEBUG] Navigated Back to: {last_file}")
        else:
            print("[DEBUG] No more history to go back.")

    def navigate_forward(self):
        """
        Navigate to the next file in history.
        """
        if self.history_forward:
            next_file = self.history_forward.pop()
            self.history_back.append(self.current_file_path)
            print(f"[DEBUG] Popped from Forward History: {next_file}")
            print(f"[DEBUG] Added to Back Stack: {self.current_file_path}")
            self.load_markdown_file(next_file)
            print(f"[DEBUG] Navigated Forward to: {next_file}")
        else:
            print("[DEBUG] No more history to go forward.")

    def show_context_menu(self, position):
        """
        Show a context menu in the preview window for additional actions.
        """
        menu = QMenu(self)

        open_in_editor_action = menu.addAction("Open in Editor")
        back_action = menu.addAction("Back")
        forward_action = menu.addAction("Forward")

        back_action.setEnabled(len(self.history_back) > 0)
        forward_action.setEnabled(len(self.history_forward) > 0)

        action = menu.exec_(self.webview.mapToGlobal(position))
        print(f"[DEBUG] Context menu action triggered: {action.text() if action else 'None'}")

        if action == open_in_editor_action and self.current_file_path:
            print(f"[DEBUG] Emitting 'file_selected_for_editor' with: {self.current_file_path}")
            self.file_selected_for_editor.emit(self.current_file_path)
        elif action == back_action:
            self.navigate_back()
        elif action == forward_action:
            self.navigate_forward()
