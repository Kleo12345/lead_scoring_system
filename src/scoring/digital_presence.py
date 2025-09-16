# lead_scoring_system/src/scoring/digital_presence.py
import requests
from bs4 import BeautifulSoup
from typing import Tuple, Dict
import logging
import time

class DigitalPresenceScorer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def score_website_quality(self, url: str) -> Tuple[int, Dict]:
        """Score website quality using free web scraping (0-25 points)"""
        score = 0
        opportunities = {
            'needs_redesign': False,
            'needs_mobile_optimization': False,
            'needs_seo': False,
            'missing_online_booking': False
        }
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = response.text.lower()
            
            # Mobile responsiveness check
            viewport_meta = soup.find('meta', {'name': 'viewport'})
            if viewport_meta and 'width=device-width' in str(viewport_meta):
                score += 5
            else:
                opportunities['needs_mobile_optimization'] = True
                
            # SEO basics
            meta_description = soup.find('meta', {'name': 'description'})
            title_tag = soup.find('title')
            if meta_description and title_tag:
                score += 3
            else:
                opportunities['needs_seo'] = True
                
            # Online booking capability
            booking_keywords = ['book', 'schedule', 'appointment', 'class', 'reserve', 'sign up']
            has_booking = any(keyword in html_content for keyword in booking_keywords)
            if has_booking:
                score += 7
            else:
                opportunities['missing_online_booking'] = True
                
            # Modern vs outdated design indicators
            outdated_indicators = [
                '<table' in html_content and 'role="presentation"' in html_content,  # Table layouts
                'jquery-1.' in html_content,  # Old jQuery
                '<font' in html_content,  # Font tags
                'comic sans' in html_content,  # Bad fonts
                len(soup.find_all('font')) > 0  # Font tags present
            ]
            
            modern_indicators = [
                'bootstrap' in html_content,
                'react' in html_content,
                'vue' in html_content,
                bool(soup.find('meta', {'property': 'og:'}))  # Social media tags
            ]
            
            if sum(outdated_indicators) >= 2:
                opportunities['needs_redesign'] = True
            elif sum(modern_indicators) >= 1:
                score += 5
                
            # SSL and basic security
            if url.startswith('https://'):
                score += 3
            
            # Content quality indicators
            img_tags = soup.find_all('img')
            if len(img_tags) > 3:  # Has images
                score += 2
                
        except Exception as e:
            logging.warning(f"Website analysis failed for {url}: {e}")
            # If website is broken/inaccessible, that's a redesign opportunity
            opportunities['needs_redesign'] = True
            score = 2  # Minimal score for broken site
            
        return min(25, score), opportunities
    
    def analyze_social_presence(self, instagram_url: str, facebook_url: str) -> Tuple[int, Dict]:
        """Basic social media presence check (0-15 points)"""
        score = 0
        social_opps = {
            'needs_social_management': False,
            'inactive_social': False
        }
        
        # Check if social links work
        for platform, url in [('instagram', instagram_url), ('facebook', facebook_url)]:
            if url and self._check_social_link(url):
                score += 3
            elif url:
                social_opps['inactive_social'] = True
        
        # If no social presence at all
        if not instagram_url and not facebook_url:
            social_opps['needs_social_management'] = True
            score = 0
        elif score < 3:
            social_opps['needs_social_management'] = True
            
        return score, social_opps
    
    def _check_social_link(self, url: str) -> bool:
        """Check if social media link is accessible"""
        try:
            response = self.session.get(url, timeout=10)
            return response.status_code == 200 and 'not found' not in response.text.lower()
        except:
            return False