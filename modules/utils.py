#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import socket
import platform
import requests
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def banner():
    """
    Display the tool banner
    """
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Check if logo.svg exists in the root directory
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logo.svg')
    
    if os.path.exists(logo_path):
        print(f"{Fore.CYAN}[*] SNAP - Social Network Analysis and Profiling Tool")
        print(f"{Fore.CYAN}[*] Logo available at: {logo_path}")
    else:
        # Fallback to ASCII art if SVG logo is not found
        banner_text = f'''
{Fore.RED}███████╗███╗   ██╗ █████╗ ██████╗ 
{Fore.RED}██╔════╝████╗  ██║██╔══██╗██╔══██╗
{Fore.RED}███████╗██╔██╗ ██║███████║██████╔╝
{Fore.RED}╚════██║██║╚██╗██║██╔══██║██╔═══╝ 
{Fore.RED}███████║██║ ╚████║██║  ██║██║     
{Fore.RED}╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     
'''
        print(banner_text)
    
    # Common information displayed regardless of logo presence
    info_text = f'''{Fore.CYAN}Social Network Analysis and Profiling Tool
{Fore.WHITE}Developed by: {Fore.GREEN}SayersLinux
{Fore.WHITE}Email: {Fore.GREEN}SayerLinux@gmail.com
{Fore.YELLOW}Version: 1.0.0
{Fore.RED}WARNING: Use responsibly and ethically. For educational purposes only.
'''
    
    print(info_text)

def check_connection():
    """
    Check if there is an active internet connection
    """
    try:
        # Try to connect to a reliable server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        pass
    
    try:
        # Alternative method using requests
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

def check_platform():
    """
    Check if the tool is running on Linux
    """
    return platform.system().lower() == 'linux'

def create_dir_if_not_exists(directory):
    """
    Create directory if it doesn't exist
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False

def is_valid_email(email):
    """
    Check if the email format is valid
    """
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone):
    """
    Check if the phone number format is valid (simple check)
    """
    import re
    # This is a simple pattern, can be improved for specific country formats
    pattern = r'^\+?[0-9]{8,15}$'
    return bool(re.match(pattern, phone))

def proxy_request(url, method='GET', headers=None, data=None, proxies=None, timeout=10):
    """
    Make a request through proxy with error handling
    """
    if proxies is None:
        # Use Tor proxy by default in stealth mode
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
    
    try:
        if method.upper() == 'GET':
            response = requests.get(
                url, 
                headers=headers, 
                proxies=proxies, 
                timeout=timeout
            )
        elif method.upper() == 'POST':
            response = requests.post(
                url, 
                headers=headers, 
                data=data, 
                proxies=proxies, 
                timeout=timeout
            )
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        return response
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Request error: {str(e)}")
        return None

def get_random_user_agent():
    """
    Return a random user agent string
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]
    
    import random
    return random.choice(user_agents)