"""
Helper utilities
"""

import json
import os
import platform
from pathlib import Path

def load_config():
    """Load configuration from config file"""
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.json"
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return get_default_config()

def get_default_config():
    """Get default configuration"""
    return {
        "browser": {
            "debug_port": 9222,
            "profile_paths": {
                "mac": "~/Library/Application Support/BraveSoftware/Brave-Browser",
                "windows": "~/AppData/Local/BraveSoftware/Brave-Browser/User Data",
                "linux": "~/.config/BraveSoftware/Brave-Browser"
            },
            "binary_paths": {
                "mac": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                "windows": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                "linux": "/usr/bin/brave-browser"
            }
        },
        "urls": {
            "prompt_enhancer": "https://www.maxai.co/ai-tools/ai-writer/prompt-enhancement/",
            "perplexity": "https://perplexity.ai"
        },
        "timeouts": {
            "page_load": 15,
            "element_wait": 10,
            "response_wait": 30
        },
        "project": {
            "output_directory": "~/Desktop",
            "project_prefix": "AI_Generated_"
        }
    }

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🤖 AI WEBSITE GENERATOR v2.0                   ║
║                                                              ║
║    MaxAI Enhancement + Perplexity Pro + Brave Browser       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def get_system_info():
    """Get system information"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "architecture": platform.architecture()[0]
    }
