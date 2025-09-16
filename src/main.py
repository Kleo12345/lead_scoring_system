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
from src.scoring.contact_quality import ContactQualityScorer
from src.utils.db_manager import DatabaseManager
from src.utils.config_loader import load_config
from src.free_scraper import FreeScraper
import pandas as pd
from typing import List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LeadScoringPipeline:
    def __init__(self):
        self.config = load_config()
        self.ingestion = DataIngestion()
        self.validator = DataValidator()
        self.scraper = FreeScraper()
        self.business_scorer = BusinessMetricsScorer(self.config)
        self.digital_scorer = DigitalPresenceScorer(self.scraper, self.config)
        self.engagement_scorer = EngagementScorer(self.scraper, self.config)
        self.contact_scorer = ContactQualityScorer(self.config)
        self.calculator = PriorityCalculator(self.config)
        self.db = DatabaseManager()
    
    def process_leads(self, file_paths: List[str]) -> pd.DataFrame:
        """Main processing pipeline using cleaned, lowercase column names."""
        df = self.ingestion.batch_load_files(file_paths)
        
        # --- CHANGE: Use 'email' (lowercase) ---
        df = df[df['email'].apply(self.validator.validate_email)]
        
        scored_leads = []
        
        for _, row in df.iterrows():
            # --- CHANGE: Use lowercase and underscore for all column access ---
            business_name = row['businessname']
            logging.info(f"Processing lead: {business_name}")
            
            business_score, _ = self.business_scorer.score_business_size(
                business_name, row.get('address', ''), row.get('zip', '')
            )
            
            digital_score, opportunities = self.digital_scorer.score_website_quality(
                row.get('websiteurl', '')
            )
            
            engagement_score, review_opps = self.engagement_scorer.analyze_review_opportunity(
                row.get('gmaps_url', '')
            )
            
            contact_score = self.contact_scorer.score(row.get('email', ''))
            
            scores = {
                'business_size': business_score,
                'digital_presence': digital_score,
                'engagement_opportunity': engagement_score,
                'contact_quality': contact_score,
                'tech_needs': 10 # Still hardcoded, a future improvement
            }
            
            total_score, tier, value = self.calculator.calculate_final_score(scores)
            
            scored_leads.append({
                # --- CHANGE: Standardize output column names as well ---
                'BusinessName': business_name,
                'Email': row.get('email', ''),
                'Phone': row.get('telephone', ''),
                'Website': row.get('websiteurl', ''),
                'City': row.get('city', ''),
                'TotalScore': int(total_score),
                'Tier': tier,
                'EstimatedValue': value,
                'NeedsRedesign': opportunities.get('needs_redesign', False),
                'NeedsReviews': review_opps.get('needs_review_campaign', False)
            })
        
        results_df = pd.DataFrame(scored_leads)
        if not results_df.empty:
            results_df = results_df.sort_values('TotalScore', ascending=False)
            
        # --- Save to database and CSV ---
        self.db.save_leads_dataframe(results_df)
        results_df.to_csv("data/output/scored_leads.csv", index=False)

        return results_df
        
    def cleanup(self):
        self.scraper.cleanup()

if __name__ == "__main__":
    pipeline = LeadScoringPipeline()
    try:
        file_paths = [
            "/home/john/dev/python/snow_tools/lead_scoring_system/data/Gyms in Dallas, TX (Report by Kleanth Hoxhaj).xlsx",
            # Add other file paths here if needed
        ]
        results = pipeline.process_leads(file_paths)
        if not results.empty:
            print("\n=== TOP PROSPECTS FOR NEW MARKETING AGENCY ===")
            print(results.head(10).to_string(index=False))
        else:
            print("No valid leads were processed.")
    finally:
        pipeline.cleanup()