# test_image_processing.py
import os
import base64
from io import BytesIO
from PIL import Image

def encode_image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"Image mode: {img.mode}")
            print(f"Image format: {img.format}")

            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")

            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS

            img.thumbnail((800, 800), resample)

            buffered = BytesIO()
            img_format = img.format if img.format else 'PNG'
            img.save(buffered, format=img_format)
            img_bytes = buffered.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            mime_type = Image.MIME.get(img_format, 'image/png')
            data_uri = f"data:{mime_type};base64,{img_base64}"
            print("Data URI generated successfully.")
            return data_uri
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

image_path = '/home/jamie/Programming/venv_Python/jmd_editor/images/tux.png'
data_uri = encode_image_to_base64(image_path)
if data_uri:
    print("Data URI:")
    print(data_uri[:100] + '...')  # Print first 100 characters for brevity
else:
    print("Failed to generate Data URI.")

