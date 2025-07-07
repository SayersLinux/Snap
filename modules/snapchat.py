#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore, Style, init
from .utils import proxy_request, get_random_user_agent

class SnapchatModule:
    def __init__(self):
        self.base_url = "https://www.snapchat.com/"
        self.api_url = "https://story.snapchat.com/"
        self.map_url = "https://map.snapchat.com/"
        self.headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.snapchat.com/"
        }
        self.session = requests.Session()
    
    def analyze(self, username, stealth=False, verbose=False):
        """
        Analyze Snapchat profile and gather information
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Analyzing Snapchat profile: {username}")
        
        results = {}
        
        # Get profile information
        profile_data = self._get_profile_data(username, stealth)
        if not profile_data:
            if verbose:
                print(f"{Fore.RED}[!] Failed to retrieve Snapchat profile data for {username}")
            return {}
        
        # Extract basic information
        results["username"] = username
        results["display_name"] = profile_data.get("display_name", "")
        results["bitmoji_url"] = profile_data.get("bitmoji_url", "")
        results["subscriber_count"] = profile_data.get("subscriber_count", 0)
        results["story_count"] = profile_data.get("story_count", 0)
        results["last_active"] = profile_data.get("last_active", "")
        results["snapcode_url"] = profile_data.get("snapcode_url", "")
        
        # Get recent stories if available
        stories = self._get_recent_stories(username, stealth, verbose)
        if stories:
            results["recent_stories"] = stories
        
        # Get location information if available
        location_data = self._get_location_data(username, stealth, verbose)
        if location_data:
            results["location"] = location_data
        
        # Add delay if in stealth mode
        if stealth:
            time.sleep(random.uniform(2, 5))
        
        return results
    
    def _get_profile_data(self, username, stealth=False):
        """
        Get Snapchat profile data
        """
        url = f"{self.base_url}add/{username}"
        
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
        
        try:
            # Try to extract profile data from JavaScript
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # Extract JSON data
                    json_str = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*\});', script.string)
                    if json_str:
                        data = json.loads(json_str.group(1))
                        # Navigate through the complex JSON structure to find user data
                        if 'addFriendPage' in data and 'user' in data['addFriendPage']:
                            user_data = data['addFriendPage']['user']
                            return self._parse_user_data(user_data)
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
        
        # If JavaScript parsing fails, try HTML parsing
        return self._parse_profile_html(soup, username)
    
    def _parse_user_data(self, user_data):
        """
        Parse user data from JavaScript object
        """
        profile_data = {}
        
        profile_data["display_name"] = user_data.get("displayName", "")
        profile_data["bitmoji_url"] = user_data.get("bitmojiAvatarUrl", "")
        profile_data["subscriber_count"] = user_data.get("subscriberCount", 0)
        profile_data["story_count"] = user_data.get("storyCount", 0)
        profile_data["snapcode_url"] = user_data.get("snapcodeUrl", "")
        
        # Parse last active time if available
        if "lastActiveTimestamp" in user_data:
            try:
                timestamp = int(user_data["lastActiveTimestamp"]) / 1000  # Convert to seconds
                last_active = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                profile_data["last_active"] = last_active
            except (ValueError, TypeError):
                pass
        
        return profile_data
    
    def _parse_profile_html(self, soup, username):
        """
        Parse profile data from HTML when JavaScript parsing fails
        """
        profile_data = {}
        
        # Try to extract display name
        try:
            name_element = soup.find('h1', class_=lambda c: c and 'displayName' in c)
            if name_element:
                profile_data["display_name"] = name_element.get_text(strip=True)
        except Exception:
            pass
        
        # Try to extract bitmoji image
        try:
            bitmoji_element = soup.find('img', class_=lambda c: c and 'bitmoji' in c)
            if bitmoji_element and bitmoji_element.get('src'):
                profile_data["bitmoji_url"] = bitmoji_element.get('src')
        except Exception:
            pass
        
        # Try to extract subscriber count
        try:
            subscriber_element = soup.find(string=re.compile(r'subscribers', re.IGNORECASE))
            if subscriber_element:
                parent = subscriber_element.parent
                count_text = parent.get_text(strip=True)
                count_match = re.search(r'(\d[\d,\.]*)', count_text)
                if count_match:
                    count_str = count_match.group(1).replace(',', '')
                    profile_data["subscriber_count"] = self._parse_count(count_str)
        except Exception:
            pass
        
        # Try to extract story count
        try:
            story_element = soup.find(string=re.compile(r'stories', re.IGNORECASE))
            if story_element:
                parent = story_element.parent
                count_text = parent.get_text(strip=True)
                count_match = re.search(r'(\d[\d,\.]*)', count_text)
                if count_match:
                    count_str = count_match.group(1).replace(',', '')
                    profile_data["story_count"] = self._parse_count(count_str)
        except Exception:
            pass
        
        # Try to extract snapcode image
        try:
            snapcode_element = soup.find('img', class_=lambda c: c and 'snapcode' in c)
            if snapcode_element and snapcode_element.get('src'):
                profile_data["snapcode_url"] = snapcode_element.get('src')
        except Exception:
            pass
        
        return profile_data
    
    def _get_recent_stories(self, username, stealth=False, verbose=False):
        """
        Get recent stories
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Retrieving recent stories for {username}")
            
        url = f"{self.api_url}@{username}"
        
        if stealth:
            response = proxy_request(url, headers=self.headers)
        else:
            try:
                response = self.session.get(url, headers=self.headers)
            except requests.RequestException:
                return []
        
        if not response or response.status_code != 200:
            return []
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        stories = []
        
        try:
            # Try to find stories in JavaScript
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # Extract JSON data
                    json_str = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*\});', script.string)
                    if json_str:
                        data = json.loads(json_str.group(1))
                        # Navigate through the complex JSON structure to find stories
                        if 'storyPage' in data and 'stories' in data['storyPage']:
                            story_data = data['storyPage']['stories']
                            for story_id, story in story_data.items():
                                story_obj = {
                                    "id": story_id,
                                    "timestamp": self._format_timestamp(story.get('timestamp')),
                                    "duration": story.get('duration', 0),
                                    "type": story.get('mediaType', 'unknown'),
                                    "view_count": story.get('viewCount', 0)
                                }
                                stories.append(story_obj)
                                if len(stories) >= 5:  # Limit to 5 recent stories
                                    break
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
        
        # If JavaScript parsing fails, try HTML parsing
        if not stories:
            stories = self._parse_stories_html(soup, username)
        
        return stories[:5]  # Limit to 5 recent stories
    
    def _parse_stories_html(self, soup, username):
        """
        Parse stories from HTML when JavaScript parsing fails
        """
        stories = []
        
        try:
            # Find story containers
            story_elements = soup.select('div[data-testid="story-item"]')
            
            for element in story_elements:
                timestamp_element = element.select_one('time')
                timestamp = ""
                if timestamp_element and timestamp_element.get('datetime'):
                    timestamp = timestamp_element.get('datetime')
                
                # Try to get story type (image/video)
                story_type = "unknown"
                if element.find('video'):
                    story_type = "video"
                elif element.find('img'):
                    story_type = "image"
                
                story_obj = {
                    "id": f"story_{len(stories)}",
                    "timestamp": timestamp,
                    "type": story_type
                }
                
                stories.append(story_obj)
                if len(stories) >= 5:  # Limit to 5 recent stories
                    break
        except Exception:
            pass
            
        return stories
    
    def _get_location_data(self, username, stealth=False, verbose=False):
        """
        Get location data if available on Snap Map
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Checking location data for {username}")
            
        # This is a placeholder as direct access to location data is limited
        # In a real implementation, this would use the Snap Map API if available
        return None
    
    def _parse_count(self, count_text):
        """
        Parse count text (e.g., "1.5K", "2M") to integer
        """
        try:
            count_text = count_text.replace(',', '')
            if 'K' in count_text or 'k' in count_text:
                return int(float(count_text.replace('K', '').replace('k', '')) * 1000)
            elif 'M' in count_text or 'm' in count_text:
                return int(float(count_text.replace('M', '').replace('m', '')) * 1000000)
            else:
                return int(count_text)
        except (ValueError, TypeError):
            return 0
    
    def _format_timestamp(self, timestamp):
        """
        Format timestamp to readable date/time
        """
        if not timestamp:
            return ""
            
        try:
            # Convert to seconds if in milliseconds
            if len(str(timestamp)) > 10:
                timestamp = int(timestamp) / 1000
                
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return ""