"""
File Generator Utility

Helper functions to generate dummy files for test automation.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

class FileGenerator:
    """Generates dummy files for testing."""
    
    @staticmethod
    def generate_test_image(file_path: str, size: tuple = (100, 100), color: str = 'red') -> str:
        """
        Generate a dummy JPG image.
        
        Args:
            file_path: Absolute path to save the file
            size: Tuple of (width, height)
            color: Color name or hex
            
        Returns:
            str: Absolute path to the generated file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create a new image with the given color
            img = Image.new('RGB', size, color=color)
            
            # Optional: Add text
            d = ImageDraw.Draw(img)
            try:
                # Use default font
                d.text((10, 10), "Test Image", fill="white")
            except Exception:
                pass
                
            # Save the image
            img.save(file_path)
            logger.info(f"Generated test image at: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to generate test image: {e}")
            raise

# Export instance
file_generator = FileGenerator()
