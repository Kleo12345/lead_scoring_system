# lead_scoring_system/src/scoring/priority_calculator.py
from typing import Dict, Tuple

class PriorityCalculator:
    def __init__(self, config: Dict):
        """
        Initialize PriorityCalculator with configuration.
        
        Parameters:
            config (Dict): Configuration dict containing three required sections:
                - 'scoring_weights': mapping of score keys to weight values (used to compute the weighted total).
                - 'tier_thresholds': numeric thresholds for tiers (expects keys like 'hot', 'warm', 'cold').
                - 'tier_definitions': mapping of tier keys to metadata (each should provide at least 'name' and/or 'value').
        
        Raises:
            KeyError: If any required section is missing or falsy in `config`. Error messages:
                "Config is missing 'scoring_weights' section."
                "Config is missing 'tier_thresholds' section."
                "Config is missing 'tier_definitions' section."
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
        """
        Compute a weighted final score from input feature scores and map it to a configured tier.
        
        Scores are weighted using the calculator's configured `scoring_weights` (weights are taken for each key in that config; missing score keys default to 0). The resulting total is compared against configured `tier_thresholds` in descending order (hot, warm, cold, then low) to pick a tier key. Tier metadata (human-readable name and estimated value) are returned from the configured `tier_definitions`.
        
        Parameters:
            scores (Dict): Mapping of score keys to numeric values (e.g., feature -> score). Keys not present in this dict are treated as 0.
        
        Returns:
            Tuple[float, str, str]: (total, tier_name, estimated_value)
                - total: weighted numeric score
                - tier_name: human-readable name for the determined tier (falls back to 'Undefined Tier')
                - estimated_value: associated estimated value for the tier (falls back to 'N/A')
        """
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