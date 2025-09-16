# lead_scoring_system/src/utils/db_manager.py
import sqlite3
import pandas as pd
from typing import List

class DatabaseManager:
    def __init__(self, db_path: str = "leads.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scored_leads (
                id INTEGER PRIMARY KEY,
                business_name TEXT,
                email TEXT,
                phone TEXT,
                website_url TEXT,
                total_score INTEGER,
                tier TEXT,
                opportunities TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_scored_leads(self, leads: List[LeadScore]):
        """Save scored leads to database"""
        conn = sqlite3.connect(self.db_path)
        
        for lead in leads:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scored_leads 
                (business_name, email, phone, website_url, total_score, tier, opportunities)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead.business_name, lead.email, lead.phone, lead.website_url,
                lead.total_score, lead.tier, ','.join(lead.opportunities)
            ))
        
        conn.commit()
        conn.close()
