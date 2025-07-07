#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import random
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from .utils import proxy_request, get_random_user_agent, is_valid_phone

class PhoneFinder:
    def __init__(self):
        self.headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.session = requests.Session()
        self.search_engines = [
            "https://www.google.com/search?q={}",
            "https://www.bing.com/search?q={}",
            "https://search.yahoo.com/search?p={}",
            "https://duckduckgo.com/html/?q={}"
        ]
    
    def analyze(self, username, stealth=False, verbose=False):
        """
        Find phone numbers associated with the username
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Searching for phone numbers associated with: {username}")
        
        results = {}
        all_phones = set()
        
        # Search for phone numbers using search engines
        search_queries = [
            f'"{username}" phone',
            f'"{username}" contact',
            f'"{username}" phone number',
            f'"{username}" mobile',
            f'"{username}" contact information',
            f'"{username}" call'
        ]
        
        for query in search_queries:
            if verbose:
                print(f"{Fore.YELLOW}[*] Searching with query: {query}")
                
            # Use different search engines
            for search_engine in self.search_engines:
                if stealth:
                    # Add random delay between requests in stealth mode
                    time.sleep(random.uniform(3, 7))
                
                search_url = search_engine.format(query)
                phones_found = self._search_for_phones(search_url, stealth)
                
                if phones_found:
                    all_phones.update(phones_found)
                    
                    if stealth:
                        # Break after finding phones to minimize detection risk
                        break
        
        # Filter and validate found phone numbers
        validated_phones = []
        for phone in all_phones:
            if is_valid_phone(phone):
                validated_phones.append(phone)
        
        if validated_phones:
            results["found_phones"] = validated_phones
        
        # Add delay if in stealth mode
        if stealth:
            time.sleep(random.uniform(2, 5))
        
        return results
    
    def _search_for_phones(self, search_url, stealth=False):
        """
        Search for phone numbers using the provided search URL
        """
        if stealth:
            response = proxy_request(search_url, headers=self.headers)
        else:
            try:
                response = self.session.get(search_url, headers=self.headers)
            except requests.RequestException:
                return set()
        
        if not response or response.status_code != 200:
            return set()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        
        # Extract phone numbers
        phones = self._extract_phones(page_text)
        
        # If phones found, also check the links for additional pages to scrape
        if phones and not stealth:  # Skip additional scraping in stealth mode
            links = soup.find_all('a')
            for link in links[:5]:  # Limit to first 5 links to avoid excessive requests
                href = link.get('href')
                if not href or href.startswith('#') or 'javascript:' in href:
                    continue
                    
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    parsed_url = requests.utils.urlparse(search_url)
                    href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                
                # Skip search engine result pages
                if any(engine.split('/')[2] in href for engine in self.search_engines):
                    continue
                
                try:
                    if stealth:
                        link_response = proxy_request(href, headers=self.headers)
                        # Add delay between requests
                        time.sleep(random.uniform(2, 5))
                    else:
                        link_response = self.session.get(href, headers=self.headers, timeout=5)
                        
                    if link_response and link_response.status_code == 200:
                        link_soup = BeautifulSoup(link_response.text, 'html.parser')
                        link_text = link_soup.get_text()
                        link_phones = self._extract_phones(link_text)
                        phones.update(link_phones)
                except (requests.RequestException, Exception):
                    continue
        
        return phones
    
    def _extract_phones(self, text):
        """
        Extract phone numbers from text
        """
        # This pattern can be improved for specific country formats
        phone_patterns = [
            r'\+?[\d\-\(\)\s]{7,}',  # General international format
            r'\(\d{3}\)[\s\-]?\d{3}[\s\-]?\d{4}',  # (123) 456-7890
            r'\d{3}[\s\-]\d{3}[\s\-]\d{4}',  # 123-456-7890
            r'\+\d{1,3}[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,4}'  # +1 123 456 7890
        ]
        
        all_matches = set()
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            all_matches.update(matches)
        
        # Clean up matches
        cleaned_phones = set()
        for match in all_matches:
            # Remove non-digit characters except for leading +
            phone = re.sub(r'[^\d+]', '', match)
            if len(phone) >= 7:  # Minimum length for a valid phone number
                cleaned_phones.add(phone)
        
        return cleaned_phones
    
    def _is_likely_valid_phone(self, phone):
        """
        Check if a phone number is likely to be valid
        """
        # Remove non-digit characters except for leading +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Check length (most phone numbers are between 7 and 15 digits)
        if len(cleaned) < 7 or len(cleaned) > 15:
            return False
        
        # Check if it has too many repeating digits (likely fake)
        for digit in '0123456789':
            if digit * 4 in cleaned:  # Four or more of the same digit in a row
                return False
        
        return True