# lead_scoring_system/src/scoring/priority_calculator.py
from typing import Dict, Tuple

class PriorityCalculator:
    def __init__(self, config: Dict):
        """
        Initializes the PriorityCalculator.
        Requires 'scoring_weights', 'tier_thresholds', and 'tier_definitions' 
        sections in the provided config dictionary.
        """
        # Using .get() can provide clearer error messages if a key is missing
        self.weights = config.get('scoring_weights')
        if not self.weights:
            raise KeyError("Config is missing 'scoring_weights' section.")

        self.tiers = config.get('tier_thresholds')
        if not self.tiers:
            raise KeyError("Config is missing 'tier_thresholds' section.")

        self.tier_defs = config.get('tier_definitions')
        if not self.tier_defs:
            raise KeyError("Config is missing 'tier_definitions' section.")
    
    def calculate_final_score(self, scores: Dict) -> Tuple[float, str, str]:
        """Calculate weighted final score and assign tier based on config."""
        # Calculate the weighted sum of all provided scores
        total = sum(scores.get(key, 0) * self.weights.get(key, 0) for key in self.weights)
        
        # Determine the tier by comparing the total score against thresholds
        if total >= self.tiers.get('hot', 999): # Use .get for safety
            tier_key = 'hot'
        elif total >= self.tiers.get('warm', 999):
            tier_key = 'warm'
        elif total >= self.tiers.get('cold', 999):
            tier_key = 'cold'
        else:
            tier_key = 'low'
            
        # Look up the tier's name and estimated value from the definitions
        tier_info = self.tier_defs.get(tier_key, {})
        tier_name = tier_info.get('name', 'Undefined Tier')
        estimated_value = tier_info.get('value', 'N/A')
            
        return total, tier_name, estimated_value