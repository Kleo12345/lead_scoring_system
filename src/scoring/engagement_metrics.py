# lead_scoring_system/src/scoring/engagement_metrics.py
import re
import requests
from typing import Tuple, Dict
import logging

class EngagementScorer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def analyze_review_opportunity(self, gmaps_url: str, yelp_url: str = None) -> Tuple[int, Dict]:
        """Analyze Google Reviews opportunity using free scraping (0-20 points)"""
        score = 0
        opportunities = {
            'needs_review_campaign': False, 
            'review_count': 0,
            'average_rating': 0.0,
            'recent_reviews': False
        }
        
        try:
            if gmaps_url and 'maps.google.com' in gmaps_url:
                response = self.session.get(gmaps_url, timeout=15)
                content = response.text
                
                # Extract review count using regex patterns
                review_patterns = [
                    r'(\d+)\s*reviews?',
                    r'"reviewCount":(\d+)',
                    r'review.*?(\d+)',
                    r'(\d+).*?review'
                ]
                
                review_count = 0
                for pattern in review_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        review_count = max([int(match) for match in matches if match.isdigit()])
                        break
                
                opportunities['review_count'] = review_count
                
                # Extract star rating
                rating_patterns = [
                    r'(\d\.\d)\s*star',
                    r'"aggregateRating".*?"ratingValue":"(\d\.\d)"',
                    r'aria-label="(\d\.\d) stars"'
                ]
                
                for pattern in rating_patterns:
                    rating_matches = re.findall(pattern, content, re.IGNORECASE)
                    if rating_matches:
                        try:
                            opportunities['average_rating'] = float(rating_matches[0])
                            break
                        except:
                            continue
                
                # Score based on review count
                if review_count == 0:
                    score = 20  # Biggest opportunity
                    opportunities['needs_review_campaign'] = True
                elif review_count < 10:
                    score = 18
                    opportunities['needs_review_campaign'] = True
                elif review_count < 25:
                    score = 15
                    opportunities['needs_review_campaign'] = True
                elif review_count < 50:
                    score = 8
                else:
                    score = 3  # Already has good reviews
                    
                # Bonus for good ratings but low count
                if opportunities['average_rating'] >= 4.0 and review_count < 20:
                    score += 2
                    
        except Exception as e:
            logging.warning(f"Review analysis failed for {gmaps_url}: {e}")
            # If we can't check, assume opportunity exists
            score = 15
            opportunities['needs_review_campaign'] = True
            
        return score, opportunities
    
    def check_online_reputation(self, business_name: str, city: str) -> Tuple[int, Dict]:
        """Check online reputation using free search (0-10 points)"""
        score = 5  # Base score
        reputation_info = {
            'has_negative_results': False,
            'needs_reputation_management': False
        }
        
        try:
            # Search for business + city + "reviews" or "complaints"
            search_terms = [
                f"{business_name} {city} reviews",
                f"{business_name} {city} complaints"
            ]
            
            for term in search_terms[:1]:  # Limit to avoid too many requests
                search_url = f"https://www.google.com/search?q={term.replace(' ', '+')}"
                response = self.session.get(search_url, timeout=10)
                
                # Look for negative indicators in search results
                negative_indicators = ['complaint', 'scam', 'terrible', 'worst', 'awful', 'fraud']
                if any(indicator in response.text.lower() for indicator in negative_indicators):
                    reputation_info['has_negative_results'] = True
                    reputation_info['needs_reputation_management'] = True
                    score = 10  # High opportunity for reputation management
                    
        except Exception as e:
            logging.warning(f"Reputation check failed for {business_name}: {e}")
            
        return score, reputation_info