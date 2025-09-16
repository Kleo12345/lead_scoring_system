# lead_scoring_system/src/scoring/business_metrics.py
from typing import Tuple, Dict

class BusinessMetricsScorer:
    def __init__(self, config: Dict):
        self.scoring_config = config['business_size_scoring']
        self.chain_indicators = config['chain_indicators']
        self.premium_indicators = config['premium_indicators']
        
    def score_business_size(self, business_name: str, address: str, zip_code: str) -> Tuple[int, str]:
        """Score business size indicators based on config values."""
        score = 0
        size_category = "Small"
        
        if any(chain in business_name.lower() for chain in self.chain_indicators):
            score += self.scoring_config['chain_bonus']
            size_category = "Chain"
        
        if any(premium in business_name.lower() for premium in self.premium_indicators):
            score += self.scoring_config['premium_bonus']
            # A premium gym can also be a chain, but "Premium" is a more specific category
            size_category = "Premium"
        
        if address and ('suite' in address.lower() or 'plaza' in address.lower()):
            score += self.scoring_config['location_bonus']
        
        return score, size_category