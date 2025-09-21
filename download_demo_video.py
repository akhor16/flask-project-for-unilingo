#!/usr/bin/env python3
"""
Download a demo video for testing the application
"""

import requests
import os

def download_demo_video():
    """Download a sample video for testing"""
    demo_urls = [
        "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
        "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
        "https://file-examples.com/storage/fe68c8b7a0b7b7b7b7b7b7b/2017/10/file_example_MP4_480_1_5MG.mp4"
    ]
    
    print("🎥 Downloading demo video for testing...")
    
    for i, url in enumerate(demo_urls, 1):
        try:
            print(f"Trying URL {i}: {url}")
            response = requests.get(url, stream=True, timeout=30)
            
            if response.status_code == 200:
                filename = f"demo_video_{i}.mp4"
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(filename)
                print(f"✅ Downloaded: {filename} ({file_size} bytes)")
                print(f"📁 You can now use this local file or upload it to a file sharing service")
                return filename
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("❌ All demo URLs failed. Please use your own MP4 video URL.")
    return None

if __name__ == "__main__":
    download_demo_video()
