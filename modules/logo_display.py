#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def display_svg_logo():
    """
    Display information about the SVG logo and how to view it
    """
    # Get the path to the logo file
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logo.svg')
    
    if not os.path.exists(logo_path):
        print(f"{Fore.RED}[!] Logo file not found at: {logo_path}")
        return False
    
    print(f"{Fore.GREEN}[+] SNAP Logo Information:")
    print(f"{Fore.CYAN}[*] Logo file: {logo_path}")
    
    # Provide platform-specific instructions for viewing the logo
    system = platform.system().lower()
    if system == 'linux':
        print(f"{Fore.YELLOW}[*] To view the logo, you can use:")
        print(f"{Fore.WHITE}    - Web browser: Open the SVG file in Firefox, Chrome, etc.")
        print(f"{Fore.WHITE}    - Image viewer: 'eog logo.svg' or 'display logo.svg'")
        print(f"{Fore.WHITE}    - Terminal: Install and use 'svgconsole' or 'imgcat'")
    elif system == 'windows':
        print(f"{Fore.YELLOW}[*] To view the logo, you can use:")
        print(f"{Fore.WHITE}    - Web browser: Double-click the SVG file or open with Edge, Chrome, etc.")
        print(f"{Fore.WHITE}    - File Explorer: Simply navigate to the file location")
    elif system == 'darwin':  # macOS
        print(f"{Fore.YELLOW}[*] To view the logo, you can use:")
        print(f"{Fore.WHITE}    - Web browser: Open the SVG file in Safari, Chrome, etc.")
        print(f"{Fore.WHITE}    - Preview: Double-click the SVG file")
        print(f"{Fore.WHITE}    - Terminal: Use 'imgcat logo.svg' if iTerm2 is installed")
    
    return True

def try_display_svg_in_terminal():
    """
    Attempt to display the SVG directly in the terminal if supported
    This is experimental and depends on terminal capabilities
    """
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logo.svg')
    
    if not os.path.exists(logo_path):
        return False
    
    # Try using different methods based on the platform and available tools
    system = platform.system().lower()
    
    if system == 'linux' or system == 'darwin':
        # Check if we're in a graphical terminal that might support images
        if 'DISPLAY' in os.environ:
            # Try using terminal image viewers if available
            viewers = ['imgcat', 'catimg', 'viu']
            
            for viewer in viewers:
                try:
                    # Check if the viewer is installed
                    if os.system(f'which {viewer} > /dev/null 2>&1') == 0:
                        # Try to display the image
                        os.system(f'{viewer} {logo_path}')
                        return True
                except:
                    continue
    
    # If we couldn't display the image directly, return False
    return False

if __name__ == "__main__":
    # If this script is run directly, try to display the logo
    if not try_display_svg_in_terminal():
        display_svg_logo()