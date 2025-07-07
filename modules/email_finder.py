#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import random
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from .utils import proxy_request, get_random_user_agent, is_valid_email

class EmailFinder:
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
        Find email addresses associated with the username
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Searching for email addresses associated with: {username}")
        
        results = {}
        all_emails = set()
        
        # Generate possible email formats
        possible_emails = self._generate_possible_emails(username)
        if possible_emails:
            results["possible_emails"] = possible_emails
        
        # Search for emails using search engines
        search_queries = [
            f'"{username}" email',
            f'"{username}" contact',
            f'"{username}" "@gmail.com"',
            f'"{username}" "@yahoo.com"',
            f'"{username}" "@hotmail.com"',
            f'"{username}" "@outlook.com"',
            f'"{username}" "@protonmail.com"',
            f'"{username}" "@icloud.com"'
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
                emails_found = self._search_for_emails(search_url, stealth)
                
                if emails_found:
                    all_emails.update(emails_found)
                    
                    if stealth:
                        # Break after finding emails to minimize detection risk
                        break
        
        # Filter and validate found emails
        validated_emails = []
        for email in all_emails:
            if is_valid_email(email) and username.lower() in email.lower():
                validated_emails.append(email)
        
        if validated_emails:
            results["found_emails"] = validated_emails
        
        # Add delay if in stealth mode
        if stealth:
            time.sleep(random.uniform(2, 5))
        
        return results
    
    def _generate_possible_emails(self, username):
        """
        Generate possible email formats based on username
        """
        domains = [
            "gmail.com",
            "yahoo.com",
            "hotmail.com",
            "outlook.com",
            "protonmail.com",
            "icloud.com",
            "mail.com",
            "aol.com"
        ]
        
        possible_emails = []
        
        # Remove special characters from username
        clean_username = re.sub(r'[^a-zA-Z0-9]', '', username)
        
        for domain in domains:
            possible_emails.append(f"{username}@{domain}")
            possible_emails.append(f"{clean_username}@{domain}")
            
            # Add common variations
            possible_emails.append(f"{username}.contact@{domain}")
            possible_emails.append(f"{username}.official@{domain}")
            possible_emails.append(f"official.{username}@{domain}")
            possible_emails.append(f"contact.{username}@{domain}")
            possible_emails.append(f"info.{username}@{domain}")
            possible_emails.append(f"{username}.info@{domain}")
        
        return possible_emails
    
    def _search_for_emails(self, search_url, stealth=False):
        """
        Search for emails using the provided search URL
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
        
        # Extract emails
        emails = self._extract_emails(page_text)
        
        # If emails found, also check the links for additional pages to scrape
        if emails and not stealth:  # Skip additional scraping in stealth mode
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
                        link_emails = self._extract_emails(link_text)
                        emails.update(link_emails)
                except (requests.RequestException, Exception):
                    continue
        
        return emails
    
    def _extract_emails(self, text):
        """
        Extract email addresses from text
        """
        email_pattern = r'[\w\.-]+@[\w\.-]+\.[\w]+'  # Basic email pattern
        found_emails = set(re.findall(email_pattern, text))
        
        # Filter out common false positives
        filtered_emails = set()
        for email in found_emails:
            # Skip emails that are likely not real
            if any(domain in email.lower() for domain in ['example.com', 'domain.com', 'email.com']):
                continue
                
            # Skip very long emails (likely not real)
            if len(email) > 50:
                continue
                
            filtered_emails.add(email)
        
        return filtered_emails