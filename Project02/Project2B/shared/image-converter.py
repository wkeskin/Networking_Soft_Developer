#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMP216 - SEC 401
Networking for Software Developers - Lab 5 Part II
Group 2: 
    Aiko Bislig 
    Jacob Ferreira
    Lissette Gorrin Rodriguez
    Samer Aljundi Al Fattouhi Aljundi
    Wardatul Keskin
"""

from PIL import Image
import os
import sys
import time

class ImageConverter:
    def __init__(self, source_dir=None, target_dir=None):
        """
        Initialize the ImageConverter.
        
        Parameters:
        source_dir (str): Directory containing images to convert (default: current directory)
        target_dir (str): Directory to save converted images (default: same as source_dir)
        """
        self.source_dir = source_dir or os.getcwd()
        self.target_dir = target_dir or self.source_dir
        
        # Create target directory if it doesn't exist
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
    
    def get_image_properties(self, image_path):
        """
        Get properties of an image.
        
        Parameters:
        image_path (str): Path to the image file
        
        Returns:
        dict: Dictionary containing image properties
        """
        try:
            with Image.open(image_path) as img:
                properties = {
                    'filename': os.path.basename(image_path),
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'date_modified': time.ctime(os.path.getmtime(image_path))
                }
                return properties
        except Exception as e:
            print(f"Error getting properties for {image_path}: {e}")
            return None
    
    def convert_to_png(self, image_path, output_path=None):
        """
        Convert an image to PNG format.
        
        Parameters:
        image_path (str): Path to the source image
        output_path (str): Path for the output image (default: derive from source)
        
        Returns:
        str: Path to the converted image or None on failure
        """
        try:
            # If output path not specified, create one in the target directory
            if output_path is None:
                basename = os.path.basename(image_path)
                name, _ = os.path.splitext(basename)
                output_path = os.path.join(self.target_dir, f"{name}.png")
            
            # Open and convert the image
            with Image.open(image_path) as img:
                # Save as PNG
                img.save(output_path, 'PNG')
                print(f"Converted {os.path.basename(image_path)} -> {os.path.basename(output_path)}")
                return output_path
        
        except Exception as e:
            print(f"Error converting {image_path}: {e}")
            return None
    
    def convert_all_in_directory(self, delete_originals=False):
        """
        Convert all images in the source directory to PNG format.
        
        Parameters:
        delete_originals (bool): Whether to delete original files after conversion
        
        Returns:
        list: List of paths to converted images
        """
        converted_files = []
        
        # Get all files in the source directory
        try:
            files = [
                f for f in os.listdir(self.source_dir) 
                if os.path.isfile(os.path.join(self.source_dir, f))
            ]
            
            # Skip PNG files if source and target directories are the same
            if self.source_dir == self.target_dir:
                files = [f for f in files if not f.lower().endswith('.png')]
            
            for file in files:
                file_path = os.path.join(self.source_dir, file)
                
                try:
                    # Try to open the file as an image
                    Image.open(file_path)
                    
                    # Convert the image
                    converted_path = self.convert_to_png(file_path)
                    
                    if converted_path:
                        converted_files.append(converted_path)
                        
                        # Delete original if requested
                        if delete_originals and os.path.normpath(file_path) != os.path.normpath(converted_path):
                            os.remove(file_path)
                            print(f"Deleted original: {file}")
                
                except Exception:
                    # Skip files that can't be opened as images
                    continue
            
            return converted_files
        
        except Exception as e:
            print(f"Error converting directory: {e}")
            return converted_files

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
        target_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        converter = ImageConverter(source_dir, target_dir)
        converted = converter.convert_all_in_directory(delete_originals=False)
        
        print(f"Converted {len(converted)} images")
    else:
        print("Usage: python image_converter.py <source_dir> [target_dir]")
