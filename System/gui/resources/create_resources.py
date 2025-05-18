"""
This script creates placeholder icon images for the application.
In a real application, you'd use actual icon files.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_image(filename, size=(64, 64), color=(60, 60, 100), text=None):
    """Create a simple colored image with optional text"""
    img = Image.new('RGB', size, color=color)
    
    if text:
        draw = ImageDraw.Draw(img)
        # Use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
        draw.text(position, text, fill=(255, 255, 255), font=font)
    
    img.save(filename)
    print(f"Created {filename}")

def main():
    # Create resources if they don't exist
    #if not os.path.exists("Sentinel/gui/resources"):
        #os.makedirs("src/sentinel/gui/resources")
    
    # Create icon images
    resources = [
        ("logo.png", (128, 128), (140, 80, 200), "S"),
        ("add_camera.png", (64, 64), (80, 140, 80), "+"),
        ("search.png", (64, 64), (100, 100, 180), "🔍"),
        ("export.png", (64, 64), (180, 140, 80), "📥"),
        ("test.png", (64, 64), (80, 140, 180), "✓"),
        ("save.png", (64, 64), (80, 180, 80), "💾"),
        ("fire.png", (64, 64), (220, 60, 60), "🔥"),
        ("fight.png", (64, 64), (220, 140, 60), "👊"),
        ("accident.png", (64, 64), (220, 60, 60), "💥"),
        ("normal.png", (64, 64), (60, 180, 60), "✓"),
    ]
    
    for filename, size, color, text in resources:
        create_image(f"System/gui/resources/{filename}", size, color, text)
    
    print("Resource creation completed")

if __name__ == "__main__":
    main()