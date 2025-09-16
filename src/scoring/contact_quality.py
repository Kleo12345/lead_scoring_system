# lead_scoring_system/src/scoring/contact_quality.py
from typing import Dict

class ContactQualityScorer:
    def __init__(self, config: Dict):
        self.scoring_config = config['contact_quality_scoring']
        self.negative_keywords = set(config['negative_email_keywords'])
        self.dm_keywords = set(config['decision_maker_keywords'])
        self.personal_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}

    def score(self, email: str) -> int:
        """
        Scores an email based on predefined rules in the config.
        """
        if not email or not isinstance(email, str):
            return 0

        email_local_part = email.split('@')[0].lower()
        email_domain = email.split('@')[-1].lower()

        # Check for generic/negative keywords
        if any(keyword in email_local_part for keyword in self.negative_keywords):
            return self.scoring_config['generic_penalty']

        score = 0
        # Check for decision-maker keywords
        if any(keyword in email_local_part for keyword in self.dm_keywords):
            score += self.scoring_config['decision_maker_bonus']
        
        # Score based on domain type
        if email_domain in self.personal_domains:
            score += self.scoring_config['personal_domain_bonus']
        else:
            # Assume it's a business domain if not a common personal one
            score += self.scoring_config['business_domain_bonus']
            
        return score