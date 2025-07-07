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

class TwitterModule:
    def __init__(self):
        self.base_url = "https://twitter.com/"
        self.api_url = "https://api.twitter.com/1.1/"
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
        Analyze Twitter profile and gather information
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Analyzing Twitter profile: {username}")
        
        results = {}
        
        # Get profile information
        profile_data = self._get_profile_data(username, stealth)
        if not profile_data:
            if verbose:
                print(f"{Fore.RED}[!] Failed to retrieve Twitter profile data for {username}")
            return {}
        
        # Extract basic information
        results["username"] = username
        results["name"] = profile_data.get("name", "")
        results["bio"] = profile_data.get("bio", "")
        results["location"] = profile_data.get("location", "")
        results["website"] = profile_data.get("website", "")
        results["join_date"] = profile_data.get("join_date", "")
        results["followers_count"] = profile_data.get("followers_count", 0)
        results["following_count"] = profile_data.get("following_count", 0)
        results["tweets_count"] = profile_data.get("tweets_count", 0)
        results["profile_image_url"] = profile_data.get("profile_image_url", "")
        results["is_verified"] = profile_data.get("is_verified", False)
        
        # Extract email addresses from bio
        if results["bio"]:
            emails = self._extract_emails(results["bio"])
            if emails:
                results["emails_from_bio"] = emails
        
        # Extract phone numbers from bio
        if results["bio"]:
            phones = self._extract_phones(results["bio"])
            if phones:
                results["phones_from_bio"] = phones
        
        # Get recent tweets
        tweets = self._get_recent_tweets(username, stealth, verbose)
        if tweets:
            results["recent_tweets"] = tweets
            
            # Extract emails and phones from tweets
            all_emails = set()
            all_phones = set()
            
            for tweet in tweets:
                tweet_text = tweet.get("text", "")
                if tweet_text:
                    tweet_emails = self._extract_emails(tweet_text)
                    tweet_phones = self._extract_phones(tweet_text)
                    
                    all_emails.update(tweet_emails)
                    all_phones.update(tweet_phones)
            
            if all_emails:
                results["emails_from_tweets"] = list(all_emails)
            
            if all_phones:
                results["phones_from_tweets"] = list(all_phones)
        
        # Add delay if in stealth mode
        if stealth:
            time.sleep(random.uniform(2, 5))
        
        return results
    
    def _get_profile_data(self, username, stealth=False):
        """
        Get Twitter profile data
        """
        url = f"{self.base_url}{username}"
        
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
            # Try to find the user data in JavaScript
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # Extract JSON data
                    json_str = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*\});', script.string)
                    if json_str:
                        data = json.loads(json_str.group(1))
                        # Navigate through the complex JSON structure to find user data
                        if 'entities' in data and 'users' in data['entities']:
                            users = data['entities']['users']
                            if username.lower() in users:
                                user_data = users[username.lower()]
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
        
        profile_data["name"] = user_data.get("name", "")
        profile_data["bio"] = user_data.get("description", "")
        profile_data["location"] = user_data.get("location", "")
        profile_data["website"] = user_data.get("url", "")
        profile_data["join_date"] = user_data.get("created_at", "")
        profile_data["followers_count"] = user_data.get("followers_count", 0)
        profile_data["following_count"] = user_data.get("friends_count", 0)
        profile_data["tweets_count"] = user_data.get("statuses_count", 0)
        profile_data["profile_image_url"] = user_data.get("profile_image_url_https", "").replace("_normal", "")
        profile_data["is_verified"] = user_data.get("verified", False)
        
        return profile_data
    
    def _parse_profile_html(self, soup, username):
        """
        Parse profile data from HTML when JavaScript parsing fails
        """
        profile_data = {}
        
        # Try to extract name
        try:
            name_element = soup.find('meta', {"property": "og:title"})
            if name_element and name_element.get("content"):
                profile_data["name"] = name_element.get("content").strip()
        except Exception:
            pass
        
        # Try to extract bio
        try:
            bio_element = soup.find('meta', {"property": "og:description"})
            if bio_element and bio_element.get("content"):
                profile_data["bio"] = bio_element.get("content").strip()
        except Exception:
            pass
        
        # Try to extract profile image
        try:
            image_element = soup.find('meta', {"property": "og:image"})
            if image_element and image_element.get("content"):
                profile_data["profile_image_url"] = image_element.get("content").strip()
        except Exception:
            pass
        
        # Try to extract follower and following counts
        try:
            stat_elements = soup.select('a[href*="followers"] span, a[href*="following"] span')
            if len(stat_elements) >= 2:
                # First element is usually following count
                following_text = stat_elements[0].get_text(strip=True)
                following_count = self._parse_count(following_text)
                if following_count is not None:
                    profile_data["following_count"] = following_count
                
                # Second element is usually followers count
                followers_text = stat_elements[1].get_text(strip=True)
                followers_count = self._parse_count(followers_text)
                if followers_count is not None:
                    profile_data["followers_count"] = followers_count
        except Exception:
            pass
        
        # Try to extract verification status
        try:
            verified_badge = soup.select('svg[aria-label="Verified account"]')
            profile_data["is_verified"] = len(verified_badge) > 0
        except Exception:
            profile_data["is_verified"] = False
        
        return profile_data
    
    def _parse_count(self, count_text):
        """
        Parse count text (e.g., "1.5K", "2M") to integer
        """
        try:
            count_text = count_text.replace(',', '')
            if 'K' in count_text:
                return int(float(count_text.replace('K', '')) * 1000)
            elif 'M' in count_text:
                return int(float(count_text.replace('M', '')) * 1000000)
            else:
                return int(count_text)
        except (ValueError, TypeError):
            return None
    
    def _get_recent_tweets(self, username, stealth=False, verbose=False):
        """
        Get recent tweets
        """
        if verbose:
            print(f"{Fore.CYAN}[*] Retrieving recent tweets for {username}")
            
        url = f"{self.base_url}{username}"
        
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
        tweets = []
        
        try:
            # Try to find tweets in JavaScript
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # Extract JSON data
                    json_str = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*\});', script.string)
                    if json_str:
                        data = json.loads(json_str.group(1))
                        # Navigate through the complex JSON structure to find tweets
                        if 'entities' in data and 'tweets' in data['entities']:
                            tweet_data = data['entities']['tweets']
                            for tweet_id, tweet in tweet_data.items():
                                if tweet.get('user_id_str') == username.lower() or tweet.get('screen_name') == username.lower():
                                    tweet_obj = {
                                        "id": tweet_id,
                                        "text": tweet.get('full_text', tweet.get('text', '')),
                                        "created_at": tweet.get('created_at', ''),
                                        "retweet_count": tweet.get('retweet_count', 0),
                                        "favorite_count": tweet.get('favorite_count', 0),
                                        "url": f"https://twitter.com/{username}/status/{tweet_id}"
                                    }
                                    tweets.append(tweet_obj)
                                    if len(tweets) >= 5:  # Limit to 5 recent tweets
                                        break
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
        
        # If JavaScript parsing fails, try HTML parsing
        if not tweets:
            tweets = self._parse_tweets_html(soup, username)
        
        return tweets[:5]  # Limit to 5 recent tweets
    
    def _parse_tweets_html(self, soup, username):
        """
        Parse tweets from HTML when JavaScript parsing fails
        """
        tweets = []
        
        try:
            # Find tweet containers
            tweet_elements = soup.select('div[data-testid="tweet"]')
            
            for element in tweet_elements:
                tweet_text_element = element.select_one('div[data-testid="tweetText"]')
                if not tweet_text_element:
                    continue
                    
                tweet_text = tweet_text_element.get_text(strip=True)
                
                # Try to get tweet ID from URL
                tweet_id = ""
                link_element = element.select_one('a[href*="/status/"]')
                if link_element and link_element.get('href'):
                    tweet_id_match = re.search(r'/status/(\d+)', link_element.get('href'))
                    if tweet_id_match:
                        tweet_id = tweet_id_match.group(1)
                
                # Get engagement counts
                retweet_count = 0
                favorite_count = 0
                
                engagement_elements = element.select('div[data-testid="retweet"], div[data-testid="like"]')
                if len(engagement_elements) >= 2:
                    retweet_text = engagement_elements[0].get_text(strip=True)
                    retweet_count = self._parse_count(retweet_text) or 0
                    
                    favorite_text = engagement_elements[1].get_text(strip=True)
                    favorite_count = self._parse_count(favorite_text) or 0
                
                tweet_obj = {
                    "id": tweet_id,
                    "text": tweet_text,
                    "retweet_count": retweet_count,
                    "favorite_count": favorite_count,
                    "url": f"https://twitter.com/{username}/status/{tweet_id}" if tweet_id else ""
                }
                
                tweets.append(tweet_obj)
                if len(tweets) >= 5:  # Limit to 5 recent tweets
                    break
        except Exception:
            pass
            
        return tweets
    
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