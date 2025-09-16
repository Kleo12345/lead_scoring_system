# lead_scoring_system/src/scoring/priority_calculator.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class LeadScore:
    business_name: str
    email: str
    total_score: int
    tier: str
    opportunities: List[str]
    contact_quality: str
    estimated_value: str

class PriorityCalculator:
    def __init__(self):
        self.weights = {
            'business_size': 0.30,
            'digital_presence': 0.25,
            'engagement_opportunity': 0.20,
            'contact_quality': 0.15,
            'tech_needs': 0.10
        }
    
    def calculate_final_score(self, scores: Dict) -> LeadScore:
        """Calculate weighted final score and assign tier"""
        total = sum(scores[key] * self.weights.get(key, 0) for key in scores)
        
        # Determine tier for new marketing agency
        if total >= 80:
            tier = "HOT - High Value Prospect"
            estimated_value = "$2000-5000/month"
        elif total >= 65:
            tier = "WARM - Good Opportunity"
            estimated_value = "$1000-2500/month"
        elif total >= 45:
            tier = "COLD - Potential Client"
            estimated_value = "$500-1200/month"
        else:
            tier = "LOW - Minimal Opportunity"
            estimated_value = "<$500/month"
            
        return total, tier, estimated_value