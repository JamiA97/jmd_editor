import tkinter as tk
from tkhtmlview import HTMLLabel
from markdown import markdown


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

        # Add the HTMLLabel for Markdown rendering
        self.viewer = HTMLLabel(self.inner_frame, html="<h1>Welcome to Markdown Viewer</h1>", wrap=tk.WORD)
        self.viewer.pack(fill=tk.BOTH, expand=True)  # Ensure it expands both horizontally and vertically

        # Configure resizing for the inner frame
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(0, weight=1)

        # Make this frame responsive
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Bind canvas resizing to dynamically adjust layout
        self.canvas.bind('<Configure>', self._on_canvas_resize)

    def update_content(self, markdown_text):
        """
        Update the preview area with the new Markdown content.
        This forces the canvas, inner frame, and scroll region to refresh dynamically.
        """
        # Convert Markdown to HTML
        html_content = markdown(markdown_text)
        self.viewer.set_html(html_content)

        # Force a layout recalculation
        self._refresh_layout()

    def _on_canvas_resize(self, event):
        """
        Handle resizing of the canvas and ensure the inner frame matches its size.
        """
        # Adjust the width of the inner frame to match the canvas width
        self.canvas.itemconfig(self.inner_frame_id, width=event.width)

        # Force the HTMLLabel to match the canvas height
        self.viewer.update_idletasks()
        self.viewer.config(height=event.height)  # Dynamically adjust height
        print(f"Canvas resized: width={event.width}, height={event.height}")

        # Refresh layout after resizing
        self._refresh_layout()

    def _refresh_layout(self):
        """
        Refresh the layout to ensure the HTMLLabel and scroll region are updated.
        """
        # Update the inner frame size to match the content
        self.inner_frame.update_idletasks()
        content_height = self.viewer.winfo_reqheight()  # Get the rendered content height
        content_width = self.viewer.winfo_reqwidth()  # Get the rendered content width

        # Log the size of the HTMLLabel
        print(f"HTMLLabel size: width={content_width}, height={content_height}")

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
