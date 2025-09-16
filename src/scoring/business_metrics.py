# lead_scoring_system/src/scoring/business_metrics.py
from typing import Tuple, Dict

class BusinessMetricsScorer:
    def __init__(self, config: Dict):
        """
        Initialize BusinessMetricsScorer with configuration-driven scoring rules.
        
        Parameters:
            config (Dict): Configuration dictionary with the following required keys:
                - 'business_size_scoring' (dict): Maps scoring names to numeric bonuses; must contain
                  'chain_bonus', 'premium_bonus', and 'location_bonus'.
                - 'chain_indicators' (Iterable[str]): Substrings used to detect chain businesses.
                - 'premium_indicators' (Iterable[str]): Substrings used to detect premium businesses.
        
        Notes:
            - The constructor does not validate presence or types of the keys; missing keys will raise a KeyError.
        """
        self.scoring_config = config['business_size_scoring']
        self.chain_indicators = config['chain_indicators']
        self.premium_indicators = config['premium_indicators']
        
    def score_business_size(self, business_name: str, address: str, zip_code: str) -> Tuple[int, str]:
        """
        Score a business for size-related indicators using the instance scoring configuration.
        
        Matches business_name (case-insensitive) against configured chain and premium indicators and applies bonuses from self.scoring_config:
        - Adds self.scoring_config['chain_bonus'] and sets category "Chain" if any chain indicator matches.
        - Adds self.scoring_config['premium_bonus'] and sets category "Premium" if any premium indicator matches (overrides "Chain").
        - Adds self.scoring_config['location_bonus'] if address contains "suite" or "plaza" (case-insensitive).
        
        Parameters:
            business_name (str): Business name to evaluate.
            address (str): Address used to detect location features (suite/plaza).
            zip_code (str): Included for compatibility; not used by this method.
        
        Returns:
            tuple[int, str]: (score, size_category) where size_category is "Small", "Chain", or "Premium".
        """
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