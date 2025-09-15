"""
Brave Browser Controller
Handles connection to existing Brave browser instance with user's profile
"""

import os
import time
import subprocess
import platform
import socket
import requests
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BraveController:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.driver = None
        self.original_tabs = []
        self.debug_port = config['browser']['debug_port']
        
    def connect_to_browser(self):
        """Connect to existing Brave browser or launch with user's profile"""
        try:
            # First, ensure all Brave processes are closed
            self._close_brave_instances()
            time.sleep(2)
            
            # Launch Brave with YOUR actual profile
            if self._launch_brave_with_user_profile():
                print("  ⏳ Waiting for Brave to start with your profile...")
                time.sleep(5)  # Give Brave time to fully start
                
                # Test the debugging connection
                if self._test_debug_connection():
                    print("  ✅ Debug connection verified!")
                    return self._connect_to_existing()
                else:
                    print("  ❌ Debug connection failed")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Browser connection failed: {e}")
            print(f"  ❌ Connection error: {e}")
            return False

    def _close_brave_instances(self):
        """Close all Brave instances"""
        try:
            system = platform.system().lower()
            if system == "darwin":
                os.system("pkill -f 'Brave Browser' 2>/dev/null || true")
            elif system == "windows":
                os.system("taskkill /f /im brave.exe 2>NUL || true")
            else:
                os.system("pkill -f brave-browser 2>/dev/null || true")
            
            print("  🧹 Closed existing Brave instances")
            time.sleep(2)  # Give time for processes to fully close
            
        except Exception as e:
            self.logger.warning(f"Error closing Brave instances: {e}")

    def _get_user_profile_paths(self):
        """Get the correct paths for user's Brave profile"""
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            binary_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
            # Parent directory (NOT the Default folder itself)
            profile_parent = os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser")
            profile_directory = "Default"  # The actual profile folder name
            
        elif system == "windows":
            binary_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
            profile_parent = os.path.expanduser("~/AppData/Local/BraveSoftware/Brave-Browser/User Data")
            profile_directory = "Default"
            
        else:  # Linux
            binary_path = "/usr/bin/brave-browser"
            profile_parent = os.path.expanduser("~/.config/BraveSoftware/Brave-Browser")
            profile_directory = "Default"
        
        return binary_path, profile_parent, profile_directory

    def _launch_brave_with_user_profile(self):
        """Launch Brave with your actual user profile (with all logins)"""
        try:
            binary_path, profile_parent, profile_directory = self._get_user_profile_paths()
            
            # Verify paths exist
            if not os.path.exists(binary_path):
                print(f"  ❌ Brave binary not found: {binary_path}")
                return False
                
            if not os.path.exists(profile_parent):
                print(f"  ❌ Profile directory not found: {profile_parent}")
                return False
            
            full_profile_path = os.path.join(profile_parent, profile_directory)
            if not os.path.exists(full_profile_path):
                print(f"  ❌ Default profile not found: {full_profile_path}")
                return False
            
            print(f"  📁 Using profile: {full_profile_path}")
            
            # Launch command with your actual profile
            cmd = [
                binary_path,
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={profile_parent}",  # Parent directory
                f"--profile-directory={profile_directory}",  # Profile folder name
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-web-security",  # Helps with automation
                "--disable-features=VizDisplayCompositor"
            ]
            
            print(f"  🚀 Launching Brave with your profile...")
            print(f"  📋 Profile path: {profile_parent}")
            print(f"  📂 Profile directory: {profile_directory}")
            
            # Launch with proper process handling
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            
            self.logger.info(f"Launched Brave with user profile (PID: {process.pid})")
            print(f"  📊 Brave launched with your profile (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch Brave with user profile: {e}")
            print(f"  ❌ Launch failed: {e}")
            return False

    def _test_debug_connection(self):
        """Test if remote debugging port is accessible"""
        try:
            # Test socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', self.debug_port))
            sock.close()
            
            if result == 0:
                # Test HTTP endpoint
                response = requests.get(f'http://localhost:{self.debug_port}/json', timeout=5)
                if response.status_code == 200:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Debug connection test failed: {e}")
            return False

    def _connect_to_existing(self):
        """Connect to the Brave instance with user profile"""
        try:
            options = Options()
            options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
            
            # Set Brave binary location
            binary_path, _, _ = self._get_user_profile_paths()
            options.binary_location = binary_path
            
            # Add additional options for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            print("  🔗 Connecting to Brave with your profile...")
            self.driver = webdriver.Chrome(options=options)
            
            # Store original tabs
            self.original_tabs = list(self.driver.window_handles)
            
            print(f"  ✅ Connected! Found {len(self.original_tabs)} existing tabs")
            print("  🎉 Using your profile with all saved logins!")
            self.logger.info("Connected to Brave browser with user profile")
            return True
            
        except Exception as e:
            self.logger.error(f"Could not connect to Brave with user profile: {e}")
            print(f"  ❌ Connection failed: {e}")
            return False

    def open_new_tab(self, url):
        """Open URL in new tab and switch to it"""
        try:
            self.driver.execute_script("window.open();")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.driver, self.config['timeouts']['page_load']).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open new tab: {e}")
            return False

    def find_element_safe(self, selector, timeout=None):
        """Safely find element with timeout"""
        if timeout is None:
            timeout = self.config['timeouts']['element_wait']
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as e:
            self.logger.warning(f"Element not found: {selector} - {e}")
            return None

    def cleanup_automation_tabs(self):
        """Close tabs created during automation"""
        try:
            current_tabs = self.driver.window_handles
            
            for handle in current_tabs:
                if handle not in self.original_tabs:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
            
            # Switch back to original tab
            if self.original_tabs:
                self.driver.switch_to.window(self.original_tabs[0])
            
            self.logger.info("Cleaned up automation tabs")
            print("  🧹 Closed automation tabs, kept your original tabs")
            
        except Exception as e:
            self.logger.error(f"Tab cleanup failed: {e}")

    def cleanup(self):
        """Clean up browser resources but keep user's browser open"""
        try:
            if self.driver:
                self.cleanup_automation_tabs()
                # Don't quit the driver - let user keep their browser open
                self.driver = None
                print("  ✅ Left your Brave browser open with your profile")
                    
        except Exception as e:
            self.logger.error(f"Browser cleanup error: {e}")
