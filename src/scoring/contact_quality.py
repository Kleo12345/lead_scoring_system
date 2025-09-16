# lead_scoring_system/src/scoring/contact_quality.py
from typing import Dict

class ContactQualityScorer:
    def __init__(self, config: Dict):
        """
        Initialize the ContactQualityScorer with configuration-driven rules and keyword sets.
        
        Parameters:
            config (Dict): Configuration mapping that must contain:
                - 'contact_quality_scoring': dict with numeric score adjustments (expects keys
                  'generic_penalty', 'decision_maker_bonus', 'personal_domain_bonus',
                  and 'business_domain_bonus').
                - 'negative_email_keywords': iterable of strings; any match in the email local
                  part triggers the generic penalty.
                - 'decision_maker_keywords': iterable of strings; matches in the email local
                  part grant the decision-maker bonus.
        
        Postconditions:
            - self.scoring_config is set to config['contact_quality_scoring'].
            - self.negative_keywords is a set built from config['negative_email_keywords'].
            - self.dm_keywords is a set built from config['decision_maker_keywords'].
            - self.personal_domains is initialized to {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}.
        """
        self.scoring_config = config['contact_quality_scoring']
        self.negative_keywords = set(config['negative_email_keywords'])
        self.dm_keywords = set(config['decision_maker_keywords'])
        self.personal_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}

    def score(self, email: str) -> int:
        """
        Compute a quality score for an email address using configured keyword and domain rules.
        
        Given an email string, returns 0 for falsy or non-string input. If any configured negative keyword appears in the local part (before '@'), returns the configured generic_penalty immediately. Otherwise, the score is the sum of:
        - decision_maker_bonus if any decision-maker keyword appears in the local part,
        - plus personal_domain_bonus if the domain is a common personal provider (e.g., gmail.com, yahoo.com, hotmail.com, outlook.com), otherwise business_domain_bonus.
        
        Parameters:
            email (str): The email address to score; expected to contain a local part and domain separated by '@'.
        
        Returns:
            int: The computed score according to the scoring configuration.
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