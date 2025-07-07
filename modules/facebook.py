#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from .utils import proxy_request, get_random_user_agent

class FacebookModule:
    def __init__(self):
        self.base_url = "https://www.facebook.com/"
        self.mobile_url = "https://m.facebook.com/"
        self.headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.session = requests.Session()
    
    def analyze(self, username, stealth=False, verbose=False):
        """
        Analyze Facebook profile and gather information
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Analyzing Facebook profile: {username}")
        
        results = {}
        
        # Try to get profile information using both desktop and mobile versions
        profile_data = self._get_profile_data(username, stealth, mobile=False)
        
        if not profile_data or not profile_data.get("name"):
            # Try mobile version if desktop version fails
            profile_data = self._get_profile_data(username, stealth, mobile=True)
        
        if not profile_data or not profile_data.get("name"):
            if verbose:
                print(f"{Fore.RED}[!] Failed to retrieve Facebook profile data for {username}")
            return {}
        
        # Extract basic information
        results["username"] = username
        results["name"] = profile_data.get("name", "")
        results["profile_url"] = profile_data.get("profile_url", "")
        results["profile_picture"] = profile_data.get("profile_picture", "")
        
        # Extract additional information if available
        if profile_data.get("about"):
            results["about"] = profile_data.get("about")
        
        if profile_data.get("work"):
            results["work"] = profile_data.get("work")
        
        if profile_data.get("education"):
            results["education"] = profile_data.get("education")
        
        if profile_data.get("location"):
            results["location"] = profile_data.get("location")
        
        if profile_data.get("hometown"):
            results["hometown"] = profile_data.get("hometown")
        
        # Extract contact information
        if profile_data.get("emails"):
            results["emails"] = profile_data.get("emails")
        
        if profile_data.get("phones"):
            results["phones"] = profile_data.get("phones")
        
        # Extract friend count if available
        if profile_data.get("friend_count"):
            results["friend_count"] = profile_data.get("friend_count")
        
        # Add delay if in stealth mode
        if stealth:
            time.sleep(random.uniform(2, 5))
        
        return results
    
    def _get_profile_data(self, username, stealth=False, mobile=False):
        """
        Get Facebook profile data
        """
        base = self.mobile_url if mobile else self.base_url
        url = f"{base}{username}"
        
        if stealth:
            response = proxy_request(url, headers=self.headers)
        else:
            try:
                response = self.session.get(url, headers=self.headers)
            except requests.RequestException:
                return None
        
        if not response or response.status_code != 200:
            return None
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        profile_data = {}
        
        # Extract profile information based on version (mobile or desktop)
        if mobile:
            return self._parse_mobile_profile(soup, username, url)
        else:
            return self._parse_desktop_profile(soup, username, url)
    
    def _parse_desktop_profile(self, soup, username, url):
        """
        Parse profile data from desktop version
        """
        profile_data = {
            "username": username,
            "profile_url": url
        }
        
        # Try to extract name
        try:
            # Look for the name in meta tags
            meta_title = soup.find('meta', property='og:title')
            if meta_title and meta_title.get('content'):
                profile_data["name"] = meta_title.get('content').split(' | ')[0].strip()
            else:
                # Alternative method to find name
                name_element = soup.find('h1', id='seo_h1_tag')
                if name_element:
                    profile_data["name"] = name_element.text.strip()
        except Exception:
            pass
        
        # Try to extract profile picture
        try:
            meta_image = soup.find('meta', property='og:image')
            if meta_image and meta_image.get('content'):
                profile_data["profile_picture"] = meta_image.get('content')
        except Exception:
            pass
        
        # Try to extract about information
        try:
            about_section = soup.find('div', {'data-pagelet': 'ProfileTileAbout'})
            if about_section:
                about_text = about_section.get_text(strip=True)
                if about_text:
                    profile_data["about"] = about_text
        except Exception:
            pass
        
        # Try to extract work information
        try:
            work_section = soup.find('div', string=re.compile(r'Work'))
            if work_section:
                work_items = work_section.find_next('div').find_all('div', recursive=False)
                work_list = [item.get_text(strip=True) for item in work_items if item.get_text(strip=True)]
                if work_list:
                    profile_data["work"] = work_list
        except Exception:
            pass
        
        # Try to extract education information
        try:
            edu_section = soup.find('div', string=re.compile(r'Education'))
            if edu_section:
                edu_items = edu_section.find_next('div').find_all('div', recursive=False)
                edu_list = [item.get_text(strip=True) for item in edu_items if item.get_text(strip=True)]
                if edu_list:
                    profile_data["education"] = edu_list
        except Exception:
            pass
        
        # Try to extract location information
        try:
            location_section = soup.find('div', string=re.compile(r'Current city'))
            if location_section:
                location_text = location_section.find_next('div').get_text(strip=True)
                if location_text:
                    profile_data["location"] = location_text
        except Exception:
            pass
        
        # Try to extract hometown information
        try:
            hometown_section = soup.find('div', string=re.compile(r'Hometown'))
            if hometown_section:
                hometown_text = hometown_section.find_next('div').get_text(strip=True)
                if hometown_text:
                    profile_data["hometown"] = hometown_text
        except Exception:
            pass
        
        # Try to extract friend count
        try:
            friends_element = soup.find('a', href=re.compile(r'/friends'))
            if friends_element:
                friends_text = friends_element.get_text(strip=True)
                friend_count_match = re.search(r'\d+', friends_text)
                if friend_count_match:
                    profile_data["friend_count"] = int(friend_count_match.group())
        except Exception:
            pass
        
        # Extract emails from the page
        emails = self._extract_emails(soup.get_text())
        if emails:
            profile_data["emails"] = emails
        
        # Extract phone numbers from the page
        phones = self._extract_phones(soup.get_text())
        if phones:
            profile_data["phones"] = phones
        
        return profile_data
    
    def _parse_mobile_profile(self, soup, username, url):
        """
        Parse profile data from mobile version
        """
        profile_data = {
            "username": username,
            "profile_url": url
        }
        
        # Try to extract name
        try:
            title_element = soup.find('title')
            if title_element:
                profile_data["name"] = title_element.text.split(' | ')[0].strip()
        except Exception:
            pass
        
        # Try to extract profile picture
        try:
            profile_img = soup.find('img', {'class': 'profpic'})
            if profile_img and profile_img.get('src'):
                profile_data["profile_picture"] = profile_img.get('src')
        except Exception:
            pass
        
        # Try to extract about information
        try:
            about_section = soup.find('div', id='bio')
            if about_section:
                about_text = about_section.get_text(strip=True)
                if about_text:
                    profile_data["about"] = about_text
        except Exception:
            pass
        
        # Try to extract work and education information
        try:
            info_sections = soup.find_all('div', {'class': 'timeline-item'})
            for section in info_sections:
                header = section.find('header')
                if not header:
                    continue
                    
                header_text = header.get_text(strip=True)
                
                if 'Work' in header_text:
                    work_items = section.find_all('div', {'class': 'item'})
                    work_list = [item.get_text(strip=True) for item in work_items if item.get_text(strip=True)]
                    if work_list:
                        profile_data["work"] = work_list
                        
                elif 'Education' in header_text:
                    edu_items = section.find_all('div', {'class': 'item'})
                    edu_list = [item.get_text(strip=True) for item in edu_items if item.get_text(strip=True)]
                    if edu_list:
                        profile_data["education"] = edu_list
                        
                elif 'Places' in header_text:
                    place_items = section.find_all('div', {'class': 'item'})
                    for item in place_items:
                        item_text = item.get_text(strip=True)
                        if 'Current City' in item_text:
                            profile_data["location"] = item_text.replace('Current City', '').strip()
                        elif 'Hometown' in item_text:
                            profile_data["hometown"] = item_text.replace('Hometown', '').strip()
        except Exception:
            pass
        
        # Try to extract friend count
        try:
            friends_element = soup.find('a', href=re.compile(r'/friends'))
            if friends_element:
                friends_text = friends_element.get_text(strip=True)
                friend_count_match = re.search(r'\d+', friends_text)
                if friend_count_match:
                    profile_data["friend_count"] = int(friend_count_match.group())
        except Exception:
            pass
        
        # Extract contact information
        try:
            contact_section = soup.find('div', id='contact-info')
            if contact_section:
                contact_text = contact_section.get_text()
                
                # Extract emails
                emails = self._extract_emails(contact_text)
                if emails:
                    profile_data["emails"] = emails
                
                # Extract phones
                phones = self._extract_phones(contact_text)
                if phones:
                    profile_data["phones"] = phones
        except Exception:
            pass
        
        # If no contact info found in specific section, try to extract from the entire page
        if not profile_data.get("emails"):
            emails = self._extract_emails(soup.get_text())
            if emails:
                profile_data["emails"] = emails
        
        if not profile_data.get("phones"):
            phones = self._extract_phones(soup.get_text())
            if phones:
                profile_data["phones"] = phones
        
        return profile_data
    
    def _extract_emails(self, text):
        """
        Extract email addresses from text
        """
        email_pattern = r'[\w\.-]+@[\w\.-]+\.[\w]+'  # Basic email pattern
        return re.findall(email_pattern, text)
    
    def _extract_phones(self, text):
        """
        Extract phone numbers from text
        """
        # This pattern can be improved for specific country formats
        phone_pattern = r'\+?[\d\-\(\)\s]{7,}'  
        matches = re.findall(phone_pattern, text)
        
        # Clean up matches
        cleaned_phones = []
        for match in matches:
            # Remove non-digit characters except for leading +
            phone = re.sub(r'[^\d+]', '', match)
            if len(phone) >= 7:  # Minimum length for a valid phone number
                cleaned_phones.append(phone)
                
        return cleaned_phones