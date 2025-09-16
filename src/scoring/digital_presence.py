# lead_scoring_system/src/scoring/digital_presence.py
from typing import Tuple, Dict
import requests
from src.free_scraper import FreeScraper

class DigitalPresenceScorer:
    def __init__(self, scraper: FreeScraper, config: Dict):
        """
        Initializes the DigitalPresenceScorer.

        Args:
            scraper: An instance of the FreeScraper for data fetching.
            config: The loaded configuration dictionary.
        """
        self.scraper = scraper
        self.config = config['digital_presence_scoring']
    
    def score_website_quality(self, url: str) -> Tuple[int, Dict]:
        """
        Scores website quality based on scraped data and config values.
        """
        if not url:
            return 0, {'needs_redesign': True}
        
        scraped_data = self.scraper.scrape_website_data(url)
        
        score = 0
        opportunities = {
            'needs_redesign': False,
            'needs_mobile_optimization': False,
            'needs_seo': False,
            'missing_online_booking': False
        }

        if not scraped_data['is_accessible']:
            opportunities['needs_redesign'] = True
            return 2, opportunities # Minimal score for a broken site

        # Score features based on values from the config file
        if scraped_data['is_mobile_friendly']:
            score += self.config['mobile_responsive']
        else:
            opportunities['needs_mobile_optimization'] = True

        if scraped_data['has_title_and_desc']:
            score += self.config['seo_basics']
        else:
            opportunities['needs_seo'] = True

        if scraped_data['has_booking_feature']:
            score += self.config['online_booking']
        else:
            opportunities['missing_online_booking'] = True
            
        if scraped_data['design_is_outdated']:
            opportunities['needs_redesign'] = True
        elif scraped_data['design_is_modern']:
            score += self.config['modern_tech']
            
        # Note: 'design_quality' from your config can be used for more nuanced logic later.
        # For now, we use modern_tech and outdated indicators.
            
        return score, opportunities
    
    def analyze_social_presence(self, instagram_url: str, facebook_url: str) -> Tuple[int, Dict]:
        """
        (This method remains unchanged for now)
        Basic social media presence check (0-15 points).
        """
        score = 0
        social_opps = {
            'needs_social_management': False,
            'inactive_social': False
        }
        
        for platform, url in [('instagram', instagram_url), ('facebook', facebook_url)]:
            if url and self._check_social_link(url):
                score += 3
            elif url:
                social_opps['inactive_social'] = True
        
        if not instagram_url and not facebook_url:
            social_opps['needs_social_management'] = True
            score = 0
        elif score < 3:
            social_opps['needs_social_management'] = True
            
        return score, social_opps
    
    def _check_social_link(self, url: str) -> bool:
        """Check if social media link is accessible."""
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            return response.status_code == 200 and 'not found' not in response.text.lower()
        except:
            return False