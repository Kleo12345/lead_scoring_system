# lead_scoring_system/src/free_scraper.py
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
# --- CHANGE: Import Edge-specific classes ---
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
# --- END CHANGE ---
import time
import logging
import re
from typing import Dict, Any

class FreeScraper:
    """A centralized scraper for all external web data, using requests and Selenium with Microsoft Edge."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        })
        self.driver = None
        self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup headless Microsoft Edge for JS-heavy sites like Google Maps."""
        try:
            # --- CHANGE: Use Edge Options ---
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(f'user-agent={self.session.headers["User-Agent"]}')
            
            logging.info("Setting up Microsoft Edge WebDriver...")
            
            # --- CHANGE: Use EdgeChromiumDriverManager and webdriver.Edge ---
            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)
            # --- END CHANGE ---
            
            self.driver.set_page_load_timeout(20) # Set a timeout
            logging.info("Microsoft Edge WebDriver setup successful.")
            
        except Exception as e:
            logging.warning(f"Selenium (Edge) setup failed: {e}. Google Maps scraping will be disabled.")
            self.driver = None
    
    def scrape_website_data(self, url: str) -> Dict[str, Any]:
        """Scrapes a website for digital presence indicators."""
        # This method is browser-agnostic and needs no changes.
        data = {
            'is_accessible': False,
            'has_ssl': url.startswith('https://'),
            'is_mobile_friendly': False,
            'has_title_and_desc': False,
            'has_booking_feature': False,
            'design_is_modern': False,
            'design_is_outdated': False,
            'has_images': False
        }
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data['is_accessible'] = True
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = response.text.lower()
            
            viewport_meta = soup.find('meta', {'name': 'viewport'})
            if viewport_meta and 'width=device-width' in str(viewport_meta):
                data['is_mobile_friendly'] = True
            
            meta_description = soup.find('meta', {'name': 'description'})
            title_tag = soup.find('title')
            if meta_description and title_tag:
                data['has_title_and_desc'] = True
                
            booking_keywords = ['book', 'schedule', 'appointment', 'class', 'reserve', 'sign up']
            data['has_booking_feature'] = any(keyword in html_content for keyword in booking_keywords)
            
            if '<table' in html_content and 'layout' in html_content:
                data['design_is_outdated'] = True
            if any(tech in html_content for tech in ['bootstrap', 'react', 'vue']):
                data['design_is_modern'] = True
            
            data['has_images'] = len(soup.find_all('img')) > 3

        except Exception as e:
            logging.warning(f"Website scraping failed for {url}: {e}")
            
        return data

    def scrape_google_maps_data(self, gmaps_url: str) -> Dict[str, Any]:
        """Scrapes Google Maps for review count and average rating using Selenium."""
        # This method is browser-agnostic and needs no changes.
        data = { 'review_count': 0, 'average_rating': 0.0 }
        
        if not self.driver or not gmaps_url or 'maps.google.com' not in gmaps_url:
            return data

        try:
            self.driver.get(gmaps_url)
            time.sleep(4)
            page_source = self.driver.page_source
            
            review_match = re.search(r'([\d,]+)\s+reviews', page_source, re.IGNORECASE)
            if review_match:
                data['review_count'] = int(review_match.group(1).replace(',', ''))
            
            rating_match = re.search(r'aria-label="([\d\.]+)\s+stars"', page_source, re.IGNORECASE)
            if rating_match:
                data['average_rating'] = float(rating_match.group(1))

        except Exception as e:
            logging.warning(f"Google Maps scraping failed for {gmaps_url}: {e}")
            
        return data

    def cleanup(self):
        """Closes the Selenium WebDriver session."""
        if self.driver:
            self.driver.quit()
            logging.info("Selenium (Edge) driver closed.")