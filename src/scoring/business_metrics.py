# lead_scoring_system/src/scoring/business_metrics.py
import re
from typing import Dict, Tuple

class BusinessMetricsScorer:
    def __init__(self):
        self.chain_indicators = ['equinox', 'la fitness', 'planet fitness', 'gold\'s gym', 'anytime fitness']
        self.premium_indicators = ['equinox', 'lifetime', 'club pilates', 'orange theory']
        
    def score_business_size(self, business_name: str, address: str, zip_code: str) -> Tuple[int, str]:
        """Score business size indicators (0-30 points)"""
        score = 0
        size_category = "Small"
        
        # Chain vs Independent
        if any(chain in business_name.lower() for chain in self.chain_indicators):
            score += 15
            size_category = "Chain"
        
        # Premium positioning
        if any(premium in business_name.lower() for premium in self.premium_indicators):
            score += 10
            size_category = "Premium"
        
        # Location indicators (high-income zip codes get higher scores)
        if address and ('suite' in address.lower() or 'plaza' in address.lower()):
            score += 5
        
        return min(30, score), size_category