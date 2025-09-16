# lead_scoring_system/src/scoring/engagement_metrics.py
from typing import Tuple, Dict
import logging
from src.free_scraper import FreeScraper

class EngagementScorer:
    def __init__(self, scraper: FreeScraper, config: Dict):
        """
        Initialize the EngagementScorer.
        
        Stores the provided scraper instance for fetching Google Maps data and extracts the
        'review_opportunity_scoring' subsection from the given configuration for use by
        scoring methods.
        
        Parameters:
            config (Dict): Full configuration dictionary; must contain the key
                'review_opportunity_scoring' whose value is a dict of scoring thresholds
                used by analyze_review_opportunity.
        """
        self.scraper = scraper
        self.config = config['review_opportunity_scoring']
    
    def analyze_review_opportunity(self, gmaps_url: str) -> Tuple[int, Dict]:
        """
        Determine a review-opportunity score and related metadata for a Google Maps listing URL using scraped data and scoring rules from the instance config.
        
        This method fetches review data via the injected scraper and maps the scraped review_count to a score using these config keys: 'no_reviews', 'few_reviews', 'moderate_reviews', and 'many_reviews'. It also sets a 'needs_review_campaign' flag when the score indicates an opportunity for a review campaign.
        
        Parameters:
            gmaps_url (str): URL of the Google Maps listing to analyze; passed to the scraper.
        
        Returns:
            tuple[int, dict]: (score, opportunities) where:
              - score: integer opportunity score derived from config thresholds.
              - opportunities: dict containing:
                  - 'needs_review_campaign' (bool): whether a review campaign is advisable.
                  - 'review_count' (int): review count taken from scraped data (defaults to 0).
                  - 'average_rating' (float): average rating from scraped data (defaults to 0.0).
        
        Notes:
            - The scraper is expected to return a mapping with 'review_count' and 'average_rating'.
            - If scraped data appears missing (review_count == 0 and average_rating == 0.0) but a gmaps_url was provided, the method treats this as a likely scraping failure and assigns the 'moderate_reviews' score from the config while marking a review campaign as needed.
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
        Assess the business's online reputation and return a simple reputation score and metadata.
        
        This is a lightweight, placeholder check that produces a base reputation score on a 0–10 scale and a minimal metadata dictionary. It does not perform network requests or search operations in its current form.
        
        Parameters:
            business_name (str): The business name used for future-enhanced reputation checks.
            city (str): The city used for future-enhanced reputation checks.
        
        Returns:
            Tuple[int, Dict]: A pair (score, reputation_info) where `score` is an integer 0–10 (higher is better) and `reputation_info` contains:
                - 'has_negative_results' (bool): Whether negative search results were found.
                - 'needs_reputation_management' (bool): Whether active reputation management is recommended.
        """
        score = 5  # Base score
        reputation_info = {
            'has_negative_results': False,
            'needs_reputation_management': False
        }
        
        # The logic for this method has not been modified yet.
        # Future improvements could include using config for keywords and scores.
        return score, reputation_info