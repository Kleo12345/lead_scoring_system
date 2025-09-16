# lead_scoring_system/src/scoring/engagement_metrics.py
from typing import Tuple, Dict
import logging
from src.free_scraper import FreeScraper

class EngagementScorer:
    def __init__(self, scraper: FreeScraper, config: Dict):
        """
        Initializes the EngagementScorer.

        Args:
            scraper: An instance of the FreeScraper for data fetching.
            config: The loaded configuration dictionary.
        """
        self.scraper = scraper
        self.config = config['review_opportunity_scoring']
    
    def analyze_review_opportunity(self, gmaps_url: str) -> Tuple[int, Dict]:
        """
        Analyze Google Reviews opportunity based on scraped data and config values.
        """
        scraped_data = self.scraper.scrape_google_maps_data(gmaps_url)
        
        score = 0
        opportunities = {
            'needs_review_campaign': False, 
            'review_count': scraped_data.get('review_count', 0),
            'average_rating': scraped_data.get('average_rating', 0.0)
        }
        
        review_count = opportunities['review_count']
        
        # Score based on review count using values from the config file
        if review_count == 0:
            score = self.config['no_reviews']
            opportunities['needs_review_campaign'] = True
        elif review_count < 10:
            score = self.config['few_reviews']
            opportunities['needs_review_campaign'] = True
        elif review_count < 25:
            score = self.config['moderate_reviews']
            opportunities['needs_review_campaign'] = True
        else:
            score = self.config['many_reviews']
            
        # If scraping failed, assign a default high-opportunity score
        if review_count == 0 and opportunities['average_rating'] == 0.0 and gmaps_url:
            score = self.config['moderate_reviews'] # Assume moderate opportunity if scraping fails
            opportunities['needs_review_campaign'] = True
            
        return score, opportunities
    
    def check_online_reputation(self, business_name: str, city: str) -> Tuple[int, Dict]:
        """
        (This method remains unchanged for now but can be enhanced in the future)
        Check online reputation using free search (0-10 points).
        """
        score = 5  # Base score
        reputation_info = {
            'has_negative_results': False,
            'needs_reputation_management': False
        }
        
        # The logic for this method has not been modified yet.
        # Future improvements could include using config for keywords and scores.
        return score, reputation_info