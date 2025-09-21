#!/usr/bin/env python3
"""
Test script to validate video URLs
"""

import requests
import time

def test_video_url(url):
    """Test if a video URL is accessible and valid"""
    print(f"🔍 Testing: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Make a HEAD request first to check if accessible
        response = requests.head(url, headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"   Content-Length: {response.headers.get('content-length', 'Unknown')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'video' in content_type or 'mp4' in content_type:
                print("   ✅ Valid video URL")
                return True
            else:
                print("   ❌ Not a video file")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Test multiple video URLs"""
    test_urls = [
        "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
        "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
        "https://file-examples.com/storage/fe68c8b7a0b7b7b7b7b7b7b/2017/10/file_example_MP4_480_1_5MG.mp4",
        "https://youtube.com/watch?v=dQw4w9WgXcQ",  # This should fail
    ]
    
    print("🧪 Testing Video URLs...")
    print("=" * 60)
    
    working_urls = []
    
    for url in test_urls:
        if test_video_url(url):
            working_urls.append(url)
        print()
        time.sleep(1)  # Be nice to servers
    
    print("=" * 60)
    print(f"✅ Working URLs: {len(working_urls)}")
    for url in working_urls:
        print(f"   {url}")
    
    if not working_urls:
        print("❌ No working URLs found. You may need to upload your own video.")

if __name__ == "__main__":
    main()
