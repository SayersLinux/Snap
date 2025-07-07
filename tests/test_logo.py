#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.logo_display import display_svg_logo, try_display_svg_in_terminal

class TestLogoDisplay(unittest.TestCase):
    def setUp(self):
        # Get the path to the logo file
        self.logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logo.svg')
    
    def test_logo_exists(self):
        """Test if the logo file exists"""
        self.assertTrue(os.path.exists(self.logo_path), "Logo file does not exist")
    
    def test_logo_is_svg(self):
        """Test if the logo file is an SVG file"""
        with open(self.logo_path, 'r') as f:
            content = f.read()
            self.assertTrue(content.startswith('<?xml'), "File does not start with XML declaration")
            self.assertTrue('<svg' in content, "File does not contain SVG tag")
    
    def test_display_svg_logo_function(self):
        """Test if the display_svg_logo function runs without errors"""
        try:
            # Redirect stdout to avoid cluttering the test output
            original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            
            result = display_svg_logo()
            self.assertTrue(result, "display_svg_logo function returned False")
        finally:
            # Restore stdout
            sys.stdout.close()
            sys.stdout = original_stdout

if __name__ == "__main__":
    unittest.main()