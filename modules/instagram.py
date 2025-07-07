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

class InstagramModule:
    def __init__(self):
        self.base_url = "https://www.instagram.com/"
        self.api_url = "https://i.instagram.com/api/v1/"
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
        Analyze Instagram profile and gather information
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Analyzing Instagram profile: {username}")
        
        results = {}
        
        # Get profile information
        profile_data = self._get_profile_data(username, stealth)
        if not profile_data:
            if verbose:
                print(f"{Fore.RED}[!] Failed to retrieve Instagram profile data for {username}")
            return {}
        
        # Extract basic information
        results["username"] = username
        results["full_name"] = profile_data.get("full_name", "")
        results["biography"] = profile_data.get("biography", "")
        results["follower_count"] = profile_data.get("edge_followed_by", {}).get("count", 0)
        results["following_count"] = profile_data.get("edge_follow", {}).get("count", 0)
        results["is_private"] = profile_data.get("is_private", False)
        results["is_verified"] = profile_data.get("is_verified", False)
        results["profile_pic_url"] = profile_data.get("profile_pic_url_hd", "")
        results["external_url"] = profile_data.get("external_url", "")
        
        # Extract email addresses from bio
        if results["biography"]:
            emails = self._extract_emails(results["biography"])
            if emails:
                results["emails_from_bio"] = emails
        
        # Extract phone numbers from bio
        if results["biography"]:
            phones = self._extract_phones(results["biography"])
            if phones:
                results["phones_from_bio"] = phones
        
        # Get recent posts if account is not private
        if not results["is_private"]:
            posts = self._get_recent_posts(username, profile_data, stealth, verbose)
            if posts:
                results["recent_posts"] = posts
                
                # Extract emails and phones from post captions
                all_emails = set()
                all_phones = set()
                
                for post in posts:
                    caption = post.get("caption", "")
                    if caption:
                        post_emails = self._extract_emails(caption)
                        post_phones = self._extract_phones(caption)
                        
                        all_emails.update(post_emails)
                        all_phones.update(post_phones)
                
                if all_emails:
                    results["emails_from_posts"] = list(all_emails)
                
                if all_phones:
                    results["phones_from_posts"] = list(all_phones)
        
        # Add delay if in stealth mode
        if stealth:
            time.sleep(random.uniform(2, 5))
        
        return results
    
    def _get_profile_data(self, username, stealth=False):
        """
        Get Instagram profile data
        """
        url = f"{self.base_url}{username}/?__a=1"
        
        if stealth:
            response = proxy_request(url, headers=self.headers)
        else:
            try:
                response = self.session.get(url, headers=self.headers)
            except requests.RequestException:
                return None
        
        if not response or response.status_code != 200:
            return None
        
        try:
            data = response.json()
            return data.get("graphql", {}).get("user", {})
        except (json.JSONDecodeError, KeyError):
            # Try alternative method - scrape from HTML
            return self._scrape_profile_data(username, stealth)
    
    def _scrape_profile_data(self, username, stealth=False):
        """
        Scrape profile data from HTML when API fails
        """
        url = f"{self.base_url}{username}/"
        
        if stealth:
            response = proxy_request(url, headers=self.headers)
        else:
            try:
                response = self.session.get(url, headers=self.headers)
            except requests.RequestException:
                return None
        
        if not response or response.status_code != 200:
            return None
        
        try:
            # Find the shared_data JSON in the HTML
            html = response.text
            shared_data_match = re.search(r'window\._sharedData = (.*?);</script>', html)
            
            if shared_data_match:
                shared_data = json.loads(shared_data_match.group(1))
                user_data = shared_data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user", {})
                return user_data
            
            # Try another pattern if the first one fails
            additional_data_match = re.search(r'window\.__additionalDataLoaded\([^,]+,\s*(\{"user":.*?\})\);', html)
            
            if additional_data_match:
                additional_data = json.loads(additional_data_match.group(1))
                return additional_data.get("user", {})
                
        except (json.JSONDecodeError, IndexError, KeyError):
            pass
            
        return {}
    
    def _get_recent_posts(self, username, profile_data, stealth=False, verbose=False):
        """
        Get recent posts data
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Retrieving recent posts for {username}")
            
        try:
            # Get user ID from profile data
            user_id = profile_data.get("id")
            if not user_id:
                return []
                
            # Get recent posts using user ID
            url = f"{self.api_url}feed/user/{user_id}/"
            
            if stealth:
                response = proxy_request(url, headers=self.headers)
            else:
                try:
                    response = self.session.get(url, headers=self.headers)
                except requests.RequestException:
                    return []
            
            if not response or response.status_code != 200:
                return []
                
            data = response.json()
            posts = []
            
            for item in data.get("items", [])[:5]:  # Limit to 5 recent posts
                post = {
                    "id": item.get("id", ""),
                    "timestamp": item.get("taken_at", 0),
                    "caption": item.get("caption", {}).get("text", "") if item.get("caption") else "",
                    "like_count": item.get("like_count", 0),
                    "comment_count": item.get("comment_count", 0),
                    "media_type": item.get("media_type", 1),  # 1=photo, 2=video
                    "url": f"https://www.instagram.com/p/{item.get('code', '')}/"
                }
                posts.append(post)
                
            return posts
                
        except (json.JSONDecodeError, KeyError):
            # Fallback to scraping if API fails
            return self._scrape_recent_posts(username, stealth)
    
    def _scrape_recent_posts(self, username, stealth=False):
        """
        Scrape recent posts when API fails
        """
        url = f"{self.base_url}{username}/"
        
        if stealth:
            response = proxy_request(url, headers=self.headers)
        else:
            try:
                response = self.session.get(url, headers=self.headers)
            except requests.RequestException:
                return []
        
        if not response or response.status_code != 200:
            return []
            
        try:
            # Find the shared_data JSON in the HTML
            html = response.text
            shared_data_match = re.search(r'window\._sharedData = (.*?);</script>', html)
            
            if not shared_data_match:
                return []
                
            shared_data = json.loads(shared_data_match.group(1))
            edges = shared_data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("edges", [])
            
            posts = []
            for edge in edges[:5]:  # Limit to 5 recent posts
                node = edge.get("node", {})
                post = {
                    "id": node.get("id", ""),
                    "timestamp": node.get("taken_at_timestamp", 0),
                    "caption": node.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", "") if node.get("edge_media_to_caption", {}).get("edges") else "",
                    "like_count": node.get("edge_liked_by", {}).get("count", 0),
                    "comment_count": node.get("edge_media_to_comment", {}).get("count", 0),
                    "media_type": 2 if node.get("is_video", False) else 1,  # 1=photo, 2=video
                    "url": f"https://www.instagram.com/p/{node.get('shortcode', '')}/"
                }
                posts.append(post)
                
            return posts
                
        except (json.JSONDecodeError, IndexError, KeyError):
            return []
    
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