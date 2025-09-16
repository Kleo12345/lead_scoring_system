# lead_scoring_system/src/main.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.ingestion import DataIngestion
from src.data.validation import DataValidator
from src.scoring.business_metrics import BusinessMetricsScorer
from src.scoring.digital_presence import DigitalPresenceScorer
from src.scoring.engagement_metrics import EngagementScorer
from src.scoring.priority_calculator import PriorityCalculator
from src.utils.db_manager import DatabaseManager
import pandas as pd

class LeadScoringPipeline:
    def __init__(self):
        self.ingestion = DataIngestion()
        self.validator = DataValidator()
        self.business_scorer = BusinessMetricsScorer()
        self.digital_scorer = DigitalPresenceScorer()
        self.engagement_scorer = EngagementScorer()
        self.calculator = PriorityCalculator()
        self.db = DatabaseManager()
    
    def process_leads(self, file_paths: List[str]) -> pd.DataFrame:
        """Main processing pipeline"""
        # Load data
        df = self.ingestion.batch_load_files(file_paths)
        
        # Validate data
        df = df[df['Email'].apply(self.validator.validate_email_syntax)]
        
        scored_leads = []
        
        for _, row in df.iterrows():
            # Calculate individual scores
            business_score, size_cat = self.business_scorer.score_business_size(
                row['BusinessName'], row['Address'], row['ZIP']
            )
            
            digital_score, opportunities = self.digital_scorer.score_website_quality(
                row['WebsiteURL']
            )
            
            engagement_score, review_opps = self.engagement_scorer.analyze_review_opportunity(
                row['Gmaps_URL']
            )
            
            # Calculate final score
            scores = {
                'business_size': business_score,
                'digital_presence': digital_score,
                'engagement_opportunity': engagement_score,
                'contact_quality': 15,  # Base score
                'tech_needs': 10
            }
            
            total_score, tier, value = self.calculator.calculate_final_score(scores)
            
            scored_leads.append({
                'BusinessName': row['BusinessName'],
                'Email': row['Email'],
                'Phone': row.get('Telephone', ''),
                'Website': row['WebsiteURL'],
                'City': row['City'],
                'TotalScore': int(total_score),
                'Tier': tier,
                'EstimatedValue': value,
                'NeedsRedesign': opportunities.get('needs_redesign', False),
                'NeedsReviews': review_opps.get('needs_review_campaign', False)
            })
        
        # Convert to DataFrame and sort by score
        results_df = pd.DataFrame(scored_leads)
        results_df = results_df.sort_values('TotalScore', ascending=False)
        
        return results_df

if __name__ == "__main__":
    # Example usage
    pipeline = LeadScoringPipeline()
    
    file_paths = [
        "data/raw/Gyms in Dallas, TX.xlsx",
        "data/raw/Gyms in Philadelphia, PA.xlsx"
    ]
    
    results = pipeline.process_leads(file_paths)
    
    # Save results
    results.to_csv("data/output/scored_leads.csv", index=False)
    
    # Print top prospects
    print("\n=== TOP PROSPECTS FOR NEW MARKETING AGENCY ===")
    print(results.head(10).to_string(index=False))
