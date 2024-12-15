from PIL import Image
import os

def compress_image(input_path, output_path, quality=75, resize=True):
    """
    Compress an image with optional resizing and metadata removal.
    Args:
        input_path: Path to the original image.
        output_path: Path to save the compressed image.
        quality: Quality of compression (1-100, lower = smaller size).
        resize: Boolean, if True resizes the image to half resolution.
    """
    try:
        with Image.open(input_path) as img:
            # Remove Metadata
            img = img.copy()
            img.info.clear()

            # Resize Image (reduce to half)
            if resize:
                new_size = (img.width // 2, img.height // 2)
                img = img.resize(new_size, Image.LANCZOS)  # Use LANCZOS directly

            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Save compressed image
            img.save(output_path, "JPEG", optimize=True, quality=quality)

            # Log size
            original_size = os.path.getsize(input_path) // 1024
            compressed_size = os.path.getsize(output_path) // 1024
            print(f"Original Size: {original_size} KB, Compressed Size: {compressed_size} KB")
        return True
    except Exception as e:
        print(f"Error compressing image: {e}")
        return False
