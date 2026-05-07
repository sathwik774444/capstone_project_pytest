#!/usr/bin/env python3
"""
Simple test to verify Selenium Grid connection.
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_grid_connection():
    """Test basic Grid connection."""
    print("🚀 Testing Selenium Grid connection...")
    
    try:
        # Configure Chrome options for Grid
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Grid capabilities
        options.set_capability("browserName", "chrome")
        options.set_capability("browserVersion", "latest")
        options.set_capability("platformName", "ANY")
        
        print("📡 Connecting to Grid at http://localhost:4444...")
        
        # Create remote driver
        driver = webdriver.Remote(
            command_executor="http://localhost:4444",
            options=options
        )
        
        print("✅ Grid driver created successfully!")
        
        # Test navigation
        print("🌐 Navigating to Google...")
        driver.get("https://www.google.com")
        
        print(f"✅ Navigation successful! Title: {driver.title}")
        
        # Test basic interaction
        print("🔍 Finding search box...")
        search_box = driver.find_element("name", "q")
        search_box.send_keys("Selenium Grid Test")
        print("✅ Search box found and text entered!")
        
        # Clean up
        print("🧹 Cleaning up...")
        driver.quit()
        
        print("🎉 Grid connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Grid connection test FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_grid_connection()
    sys.exit(0 if success else 1)
