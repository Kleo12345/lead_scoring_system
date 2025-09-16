# lead_scoring_system/src/free_scraper.py
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from typing import Optional, Dict, Any

class FreeScraper:
    """Free web scraper for gym lead analysis - no APIs required"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.driver = None
        self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup headless Chrome for JS-heavy sites"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=options
            )
        except Exception as e:
            logging.warning(f"Selenium setup failed: {e}")
    
    def scrape_website(self, url: str) -> Dict[str, Any]:
        """Scrape website for tech analysis"""
        data = {
            'accessible': False,
            'mobile_friendly': False,
            'has_ssl': url.startswith('https://'),
            'tech_stack': [],
            'has_booking': False,
            'design_quality': 'unknown'
        }
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                data['accessible'] = True
                soup = BeautifulSoup(response.content, 'html.parser')
                content = response.text.lower()
                
                # Mobile check
                viewport = soup.find('meta', {'name': 'viewport'})
                data['mobile_friendly'] = bool(viewport and 'width=device-width' in str(viewport))
                
                # Tech stack detection
                if 'wordpress' in content: data['tech_stack'].append('WordPress')
                if 'react' in content: data['tech_stack'].append('React')
                if 'bootstrap' in content: data['tech_stack'].append('Bootstrap')
                if 'jquery' in content: data['tech_stack'].append('jQuery')
                
                # Booking system check
                booking_terms = ['book', 'schedule', 'reserve', 'appointment', 'class signup']
                data['has_booking'] = any(term in content for term in booking_terms)
                
                # Design quality indicators
                if '<table' in content and 'layout' in content:
                    data['design_quality'] = 'outdated'
                elif any(modern in content for modern in ['bootstrap', 'react', 'vue']):
                    data['design_quality'] = 'modern'
                else:
                    data['design_quality'] = 'basic'
                    
        except Exception as e:
            logging.warning(f"Website scraping failed for {url}: {e}")
            
        return data
    
    def scrape_google_reviews(self, gmaps_url: str) -> Dict[str, Any]:
        """Scrape Google Maps for review data"""
        data = {
            'review_count': 0,
            'average_rating': 0.0,
            'accessible': False
        }
        
        try:
            if self.driver:
                self.driver.get(gmaps_url)
                time.sleep(3)  # Wait for JS to load
                page_source = self.driver.page_source
            else:
                response = self.session.get(gmaps_url, timeout=15)
                page_source = response.text
            
            data['accessible'] = True
            
            # Extract review count
            import re
            review_matches = re.findall(r'(\d+)\s*reviews?', page_source, re.IGNORECASE)
            if review_matches:
                data['review_count'] = max([int(match) for match in review_matches])
            
            # Extract rating
            rating_matches = re.findall(r'(\d\.\d)\s*star', page_source, re.IGNORECASE)
            if rating_matches:
                data['average_rating'] = float(rating_matches[0])
                
        except Exception as e:
            logging.warning(f"Google Maps scraping failed: {e}")
            
        return data
    
    def check_social_presence(self, instagram_url: str = None, facebook_url: str = None) -> Dict[str, Any]:
        """Basic social media presence check"""
        data = {
            'instagram_active': False,
            'facebook_active': False,
            'total_platforms': 0
        }
        
        for platform, url in [('instagram', instagram_url), ('facebook', facebook_url)]:
            if url:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200 and 'not found' not in response.text.lower():
                        data[f'{platform}_active'] = True
                        data['total_platforms'] += 1
                except:
                    pass
        
        return data
    
    def cleanup(self):
        """Close browser resources"""
        if self.driver:
            self.driver.quit()