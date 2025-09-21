#!/usr/bin/env python3
"""
Simple test script to verify the Flask app functionality
"""

import requests
import json
import time

def test_app():
    """Test the Flask application endpoints"""
    base_url = "http://localhost:5000"
    
    # Test video URL (provided in requirements)
    test_url = "https://firebasestorage.googleapis.com/v0/b/testlingo-e48de.appspot.com/o/videolingo.mp4?alt=media&token=28e6cb7d-7906-4fff-8a41-c49191c1074a"
    
    print("🧪 Testing Video Processing App...")
    print(f"Base URL: {base_url}")
    print(f"Test Video: {test_url[:50]}...")
    print("-" * 50)
    
    try:
        # Test 1: Submit URL
        print("1. Testing URL submission...")
        response = requests.post(f"{base_url}/submit_url", 
                               json={"url": test_url},
                               timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ URL submitted successfully")
            print(f"   📊 Duration: {data['video_info']['duration']:.2f}s")
            print(f"   📏 Height: {data['video_info']['height']}px")
        else:
            print(f"   ❌ URL submission failed: {response.status_code}")
            return False
        
        # Test 2: Get video info (should be cached)
        print("\n2. Testing video info retrieval...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Main page loads successfully")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
        
        print("\n🎉 Basic functionality test completed!")
        print("💡 You can now test the full app in your browser at http://localhost:5000")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the app. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_app()
