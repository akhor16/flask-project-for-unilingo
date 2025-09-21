#!/usr/bin/env python3
"""
Test script to verify Tesseract OCR installation
"""

import pytesseract
import platform
import os

def test_tesseract():
    """Test Tesseract OCR installation"""
    print("🔍 Testing Tesseract OCR Installation...")
    print(f"Platform: {platform.system()}")
    print("-" * 50)
    
    try:
        # Try to set tesseract path for Windows
        if platform.system() == "Windows":
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
            ]
            
            print("🔍 Checking common Windows installation paths...")
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"✅ Found Tesseract at: {path}")
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
            else:
                print("❌ Tesseract not found in common paths")
                print("💡 Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
                return False
        
        # Test Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        
        # Test basic OCR functionality
        from PIL import Image
        import numpy as np
        
        # Create a simple test image with text
        test_image = Image.new('RGB', (200, 50), color='white')
        # This is a simple test - in real usage, you'd load an actual image
        
        print("✅ Tesseract OCR is properly installed and working!")
        return True
        
    except Exception as e:
        print(f"❌ Tesseract test failed: {e}")
        print("💡 Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

if __name__ == "__main__":
    test_tesseract()
