# lead_scoring_system/src/scoring/digital_presence.py
from typing import Tuple, Dict
import requests
from src.free_scraper import FreeScraper

class DigitalPresenceScorer:
    def __init__(self, scraper: FreeScraper, config: Dict):
        """
        Initialize the scorer with a scraper and the full configuration.
        
        Stores the provided FreeScraper instance on self.scraper and extracts the
        'digital_presence_scoring' sub-dictionary from the supplied config into
        self.config.
        
        Parameters:
            config (Dict): Full configuration mapping. Must contain a 'digital_presence_scoring'
                key with scoring weights (e.g. 'mobile_responsive', 'seo_basics',
                'online_booking', 'modern_tech').
        """
        self.scraper = scraper
        self.config = config['digital_presence_scoring']
    
    def score_website_quality(self, url: str) -> Tuple[int, Dict]:
        """
        Compute a website quality score from scraped site metadata and return actionable opportunities.
        
        Given a site URL, this method uses the configured FreeScraper to obtain site attributes and accumulates a numeric score using weights from self.config (keys: 'mobile_responsive', 'seo_basics', 'online_booking', 'modern_tech'). It also returns an opportunities dict of boolean flags indicating recommended improvements.
        
        Special cases:
        - If `url` is falsy, returns (0, {'needs_redesign': True}).
        - If the scraper reports the site is not accessible (`scraped_data['is_accessible'] is False`), returns (2, opportunities) with 'needs_redesign' set.
        
        Expected keys in `scraped_data` (used by this method):
        - 'is_accessible' (bool)
        - 'is_mobile_friendly' (bool)
        - 'has_title_and_desc' (bool)
        - 'has_booking_feature' (bool)
        - 'design_is_outdated' (bool)
        - 'design_is_modern' (bool)
        
        Returns:
            Tuple[int, Dict]: (score, opportunities) where `score` is the summed points from enabled features and `opportunities` is a dict with these boolean keys:
                - 'needs_redesign': True if the site is inaccessible or design is outdated.
                - 'needs_mobile_optimization': True if not mobile friendly.
                - 'needs_seo': True if missing title/description.
                - 'missing_online_booking': True if no booking feature detected.
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
        Assess basic social media presence for Instagram and Facebook profiles.
        
        Returns a tuple (score, social_opps) where score is an integer 0–6 (3 points awarded for each reachable profile)
        and social_opps is a dict with two boolean flags:
        - 'needs_social_management': True when no profiles are provided or the overall presence is weak (score < 3).
        - 'inactive_social': True if at least one provided profile URL appears inaccessible.
        
        Notes:
        - Each provided URL is checked via self._check_social_link; reachable profiles add 3 points each.
        - If neither URL is supplied, score is 0 and 'needs_social_management' is set.
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
        """
        Check whether a social media URL is reachable and likely active.
        
        Performs an HTTP GET to the given URL and returns True only if the response status code is 200 and the response body does not contain the phrase "not found" (case-insensitive). Any network error, non-200 status, or detection of "not found" in the response results in False.
        
        Parameters:
            url (str): The full URL of the social media profile or page.
        
        Returns:
            bool: True if the link appears accessible and active; False otherwise.
        """
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            return response.status_code == 200 and 'not found' not in response.text.lower()
        except:
            return False