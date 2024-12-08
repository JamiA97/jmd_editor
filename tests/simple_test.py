# test_pillow.py
from PIL import Image

image_path = '/home/jamie/Programming/venv_Python/jmd_editor/images/tux.png'

try:
    with Image.open(image_path) as img:
        img.verify()  # Verify that it's a valid image
    print("Image is valid and recognized by Pillow.")
except Exception as e:
    print(f"Error processing image {image_path}: {e}")