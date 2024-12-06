import os
import tkinter as tk
from tkinterweb import HtmlFrame  # Import HtmlFrame from tkinterweb
from markdown import markdown
from mdx_math import MathExtension
import webbrowser

# Define color variables
BACKGROUND = "#FFFFEE"  # Light cream background
TEXT_COLOR = "#222"  # Dark text color


class ViewerFrame(tk.Frame):
    def __init__(self, parent, custom_font=None):
        super().__init__(parent)

        # Store the custom font
        self.custom_font = custom_font

        # Create a frame to hold controls
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(fill=tk.X)

        # Add a "Back" button
        self.back_button = tk.Button(self.control_frame, text="Back", command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.back_button.config(state=tk.DISABLED)  # Initially disabled

        # Add the HtmlFrame for Markdown rendering
        self.viewer = HtmlFrame(self)
        self.viewer.pack(fill=tk.BOTH, expand=True)

        # Store the current Markdown content
        self.current_markdown = ""

        # Bind link click event to open links in the viewer
        self.viewer.on_link_click(self.open_link)

    def update_content(self, markdown_text):
        """
        Update the preview area with the new Markdown content and enable LaTeX rendering using KaTeX.
        """
        self.current_markdown = markdown_text  # Store the current Markdown
        self.back_button.config(state=tk.DISABLED)  # Disable the "Back" button

        # Convert Markdown to HTML with the math extension
        html_content = markdown(
            markdown_text,
            extensions=[
                'extra',          # For extra Markdown syntax
                'codehilite',     # For code highlighting
                MathExtension()   # For LaTeX rendering
            ]
        )

        # KaTeX script for rendering LaTeX
        katex_script = """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css">
        <script defer src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js"></script>
        <script defer src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js"
                onload="renderMathInElement(document.body);"></script>
        """

        # Apply custom styles for font, text color, and background color
        font_family = self.custom_font.actual("family") if self.custom_font else "Arial"
        style = f"""
        <style>
            body {{
                font-family: '{font_family}';
                font-size: 14px;
                color: {TEXT_COLOR};
                background-color: {BACKGROUND};
            }}
        </style>
        """

        # Combine the KaTeX script, styles, and HTML content
        html_with_styles = katex_script + style + html_content

        # Load the styled and KaTeX-enabled HTML
        self.viewer.load_html(html_with_styles)

    def open_link(self, url):
        """
        Handle link clicks.
        - Open HTTP/HTTPS links in the system's default web browser.
        - Render local Markdown files in the viewer.
        """
        print(f"A link to '{url}' has been clicked.")

        if url.startswith("http://") or url.startswith("https://"):
            # Open web links in the default browser
            webbrowser.open(url)
            self.back_button.config(state=tk.NORMAL)  # Enable "Back" button
        elif url.startswith("file://"):
            # Handle local files
            local_path = url[7:]  # Remove 'file://' prefix
            if local_path.endswith(".md"):
                try:
                    # Read the Markdown file and render it
                    with open(local_path, "r", encoding="utf-8") as file:
                        markdown_content = file.read()
                    self.update_content(markdown_content)
                    self.back_button.config(state=tk.NORMAL)  # Enable "Back" button
                except Exception as e:
                    print(f"Error loading local Markdown file: {e}")
            else:
                print(f"Unsupported file type: {local_path}")
        else:
            # Load other links in the HtmlFrame
            self.viewer.load_url(url)
            self.back_button.config(state=tk.NORMAL)  # Enable "Back" button

    def go_back(self):
        """
        Return to the original Markdown preview.
        """
        if self.current_markdown:
            self.update_content(self.current_markdown)  # Reload the Markdown preview
