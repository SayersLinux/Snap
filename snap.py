#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
SNAP - Social Network Analysis and Profiling Tool
Developed by: SayersLinux
Email: SayerLinux@gmail.com
'''

import os
import sys
import time
import json
import argparse
import requests
import socket
import re
import threading
from colorama import Fore, Style, init
from modules.instagram import InstagramModule
from modules.facebook import FacebookModule
from modules.twitter import TwitterModule
from modules.snapchat import SnapchatModule
from modules.email_finder import EmailFinder
from modules.phone_finder import PhoneFinder
from modules.utils import banner, check_connection, check_platform
from modules.logo_display import display_svg_logo, try_display_svg_in_terminal

# Initialize colorama
init(autoreset=True)

class Snap:
    def __init__(self):
        self.modules = {
            'instagram': InstagramModule(),
            'facebook': FacebookModule(),
            'twitter': TwitterModule(),
            'snapchat': SnapchatModule(),
            'email': EmailFinder(),
            'phone': PhoneFinder()
        }
        self.results = {}
        self.target = None
        self.output_file = None
        self.verbose = False
        self.stealth_mode = False

    def parse_args(self):
        parser = argparse.ArgumentParser(description='SNAP - Social Network Analysis and Profiling Tool')
        parser.add_argument('-u', '--username', help='Target username', required=True)
        parser.add_argument('-o', '--output', help='Output file to save results')
        parser.add_argument('-v', '--verbose', help='Enable verbose output', action='store_true')
        parser.add_argument('-s', '--stealth', help='Enable stealth mode (slower but more secure)', action='store_true')
        parser.add_argument('-p', '--platforms', help='Specific platforms to analyze (comma separated)', default='all')
        
        args = parser.parse_args()
        self.target = args.username
        self.output_file = args.output
        self.verbose = args.verbose
        self.stealth_mode = args.stealth
        
        if args.platforms.lower() == 'all':
            self.enabled_modules = list(self.modules.keys())
        else:
            self.enabled_modules = [p.strip().lower() for p in args.platforms.split(',')]
            # Validate platforms
            for platform in self.enabled_modules:
                if platform not in self.modules:
                    print(f"{Fore.RED}[!] Error: Unknown platform '{platform}'. Available platforms: {', '.join(self.modules.keys())}")
                    sys.exit(1)
    
    def run(self):
        # Check internet connection
        if not check_connection():
            print(f"{Fore.RED}[!] Error: No internet connection.")
            sys.exit(1)
            
        # Display banner
        banner()
        
        # Try to display the SVG logo in terminal if possible
        try_display_svg_in_terminal()
        
        # Display logo information
        if self.verbose:
            display_svg_logo()
        
        print(f"{Fore.CYAN}[*] Target: {Fore.WHITE}{self.target}")
        print(f"{Fore.CYAN}[*] Stealth Mode: {Fore.WHITE}{'Enabled' if self.stealth_mode else 'Disabled'}")
        print(f"{Fore.CYAN}[*] Platforms: {Fore.WHITE}{', '.join(self.enabled_modules)}")
        print(f"{Fore.CYAN}[*] Starting scan...\n")
        
        # Run each enabled module
        threads = []
        for module_name in self.enabled_modules:
            if self.verbose:
                print(f"{Fore.YELLOW}[*] Starting module: {module_name}")
            
            # Create thread for each module
            t = threading.Thread(
                target=self._run_module, 
                args=(module_name,)
            )
            threads.append(t)
            t.start()
            
            # If in stealth mode, add delay between module execution
            if self.stealth_mode and module_name != self.enabled_modules[-1]:
                time.sleep(3)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Display and save results
        self._display_results()
        if self.output_file:
            self._save_results()
    
    def _run_module(self, module_name):
        try:
            module = self.modules[module_name]
            results = module.analyze(self.target, stealth=self.stealth_mode, verbose=self.verbose)
            self.results[module_name] = results
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}[!] Error in {module_name} module: {str(e)}")
            self.results[module_name] = {'error': str(e)}
    
    def _display_results(self):
        print(f"\n{Fore.GREEN}[+] Scan Results for {self.target}:\n")
        
        for module_name, results in self.results.items():
            print(f"{Fore.YELLOW}[+] {module_name.upper()} Results:")
            
            if 'error' in results:
                print(f"  {Fore.RED}Error: {results['error']}")
                continue
                
            if not results:
                print(f"  {Fore.YELLOW}No results found.")
                continue
                
            for key, value in results.items():
                if isinstance(value, list):
                    print(f"  {Fore.CYAN}{key}:")
                    for item in value:
                        print(f"    {Fore.WHITE}- {item}")
                else:
                    print(f"  {Fore.CYAN}{key}: {Fore.WHITE}{value}")
            print()
    
    def _save_results(self):
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=4)
            print(f"{Fore.GREEN}[+] Results saved to {self.output_file}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error saving results: {str(e)}")

if __name__ == "__main__":
    try:
        snap = Snap()
        snap.parse_args()
        snap.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Scan interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] An unexpected error occurred: {str(e)}")
        sys.exit(1)