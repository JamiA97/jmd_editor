# viewer_frame.py
import os
import re
import base64
from io import BytesIO
import tkinter as tk
from tkinterweb import HtmlFrame  # Import HtmlFrame from tkinterweb
from markdown import markdown
from PIL import Image


class ViewerFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")  # Use grid for resizing

        # Add a vertical scrollbar
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")  # Attach scrollbar next to canvas

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas
        self.inner_frame = tk.Frame(self.canvas)
        self.inner_frame_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Add the HtmlFrame for Markdown rendering
        self.viewer = HtmlFrame(self.inner_frame, horizontal_scrollbar="auto")
        self.viewer.pack(fill=tk.BOTH, expand=True)  # Ensure it expands both horizontally and vertically

        # Configure resizing for the inner frame
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(0, weight=1)

        # Make this frame responsive
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Bind canvas resizing to dynamically adjust layout
        self.canvas.bind('<Configure>', self._on_canvas_resize)

        # Keep references to PhotoImage objects to prevent garbage collection
        self.image_refs = {}

    def update_content(self, markdown_text):
        """
        Update the preview area with the new Markdown content.
        This forces the canvas, inner frame, and scroll region to refresh dynamically.
        """
        # Preprocess image paths and embed as Base64
        markdown_text = self._process_image_paths(markdown_text)

        # Convert Markdown to HTML
        html_content = markdown(markdown_text, extensions=['extra', 'codehilite'])

        # Debug: Print the generated HTML content
        print("Generated HTML Content:")
        print(html_content)

        # Correct method to load HTML content
        self.viewer.load_html(html_content)

        # Force a layout recalculation
        self._refresh_layout()

    def _process_image_paths(self, markdown_text):
        """
        Preprocess Markdown to handle local image paths by converting them to Base64 data URIs.
        """

        # Match Markdown image syntax ![alt text](path)
        image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")

        def replace_with_base64(match):
            alt_text = match.group(1)
            image_path = match.group(2)

            print(f"Processing image: {image_path}")

            # Check if the image path is a URL
            if image_path.startswith('http://') or image_path.startswith('https://'):
                # For remote images, skip embedding and keep the original path
                print(f"Skipping remote image: {image_path}")
                return match.group(0)

            # Resolve the image path relative to the current working directory
            abs_image_path = os.path.abspath(image_path)

            if not os.path.exists(abs_image_path):
                print(f"Image not found: {abs_image_path}")
                return f"![{alt_text}](Image not found: {image_path})"

            try:
                # Determine the resampling filter based on Pillow version
                try:
                    resample = Image.Resampling.LANCZOS
                except AttributeError:
                    # For Pillow versions < 10.0.0
                    resample = Image.LANCZOS

                # Open the image and convert to Base64
                with Image.open(abs_image_path) as img:
                    print(f"Image mode: {img.mode}")
                    print(f"Image format: {img.format}")

                    # Convert image to RGB or RGBA if it's in a different mode
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGBA")

                    # Optionally, resize the image to a reasonable size
                    img.thumbnail((800, 800), resample)

                    buffered = BytesIO()
                    img_format = img.format if img.format else 'PNG'
                    img.save(buffered, format=img_format)
                    img_bytes = buffered.getvalue()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    mime_type = Image.MIME.get(img_format, 'image/png')
                    data_uri = f"data:{mime_type};base64,{img_base64}"
                    print(f"Successfully processed image: {abs_image_path}")
                    return f'![{alt_text}]({data_uri})'
            except Exception as e:
                print(f"Error processing image {abs_image_path}: {e}")
                return f"![{alt_text}](Error loading image: {image_path})"

        # Replace all image paths in the markdown text
        return image_pattern.sub(replace_with_base64, markdown_text)

    def _on_canvas_resize(self, event):
        """
        Handle resizing of the canvas and ensure the inner frame matches its size.
        """
        # Adjust the width of the inner frame to match the canvas width
        self.canvas.itemconfig(self.inner_frame_id, width=event.width)

        # Force the HtmlFrame to match the canvas height
        self.viewer.update_idletasks()
        self.viewer.config(width=event.width, height=event.height)  # Dynamically adjust size
        print(f"Canvas resized: width={event.width}, height={event.height}")

        # Refresh layout after resizing
        self._refresh_layout()

    def _refresh_layout(self):
        """
        Refresh the layout to ensure the HtmlFrame and scroll region are updated.
        """
        # Update the inner frame size to match the content
        self.inner_frame.update_idletasks()
        content_height = self.viewer.winfo_reqheight()  # Get the rendered content height
        content_width = self.viewer.winfo_reqwidth()  # Get the rendered content width

        # Log the size of the HtmlFrame
        print(f"HtmlFrame size: width={content_width}, height={content_height}")

        # Update the inner_frame size in the canvas
        self.canvas.itemconfig(self.inner_frame_id, height=content_height, width=content_width)

        # Log the updated inner_frame size
        print(f"Inner frame updated: width={content_width}, height={content_height}")

        # Update the scrollable region of the canvas
        self._update_scroll_region()

    def _update_scroll_region(self):
        """
        Update the scrollable region of the canvas to match its content.
        """
        self.canvas.update_idletasks()
        scroll_region = self.canvas.bbox("all")
        self.canvas.config(scrollregion=scroll_region)

        # Log the updated scroll region
        print(f"Scroll region updated: {scroll_region}")
