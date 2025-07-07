#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.snapchat import SnapchatModule

class TestSnapchatModule(unittest.TestCase):
    def setUp(self):
        self.snapchat = SnapchatModule()
        self.test_username = "snapchat"  # Official Snapchat account for testing
    
    def test_module_initialization(self):
        """Test if the module initializes correctly"""
        self.assertIsNotNone(self.snapchat)
        self.assertEqual(self.snapchat.base_url, "https://www.snapchat.com/")
        self.assertEqual(self.snapchat.api_url, "https://story.snapchat.com/")
    
    def test_parse_count(self):
        """Test the count parsing functionality"""
        self.assertEqual(self.snapchat._parse_count("1.5K"), 1500)
        self.assertEqual(self.snapchat._parse_count("2M"), 2000000)
        self.assertEqual(self.snapchat._parse_count("500"), 500)
        self.assertEqual(self.snapchat._parse_count("invalid"), 0)
    
    def test_format_timestamp(self):
        """Test the timestamp formatting functionality"""
        # Test with milliseconds timestamp
        self.assertTrue(len(self.snapchat._format_timestamp(1623766800000)) > 0)
        # Test with seconds timestamp
        self.assertTrue(len(self.snapchat._format_timestamp(1623766800)) > 0)
        # Test with invalid timestamp
        self.assertEqual(self.snapchat._format_timestamp(None), "")
        self.assertEqual(self.snapchat._format_timestamp("invalid"), "")

if __name__ == "__main__":
    unittest.main()