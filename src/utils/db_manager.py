# lead_scoring_system/src/utils/db_manager.py
import sqlite3
import pandas as pd
import logging
from typing import Set

class DatabaseManager:
    def __init__(self, db_path: str = "leads.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """
        Initialize database table. 
        The email column is now set to UNIQUE to prevent duplicate entries.
        Added columns for City and EstimatedValue to match pipeline output.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scored_leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    BusinessName TEXT NOT NULL,
                    Email TEXT NOT NULL UNIQUE,
                    Phone TEXT,
                    Website TEXT,
                    City TEXT,
                    TotalScore INTEGER,
                    Tier TEXT,
                    EstimatedValue TEXT,
                    Opportunities TEXT,
                    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database initialization failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_existing_emails(self) -> Set[str]:
        """Fetches all unique emails currently stored in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Use pandas for efficient querying
            df = pd.read_sql_query("SELECT Email FROM scored_leads", conn)
            return set(df['Email'].unique())
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            logging.error(f"Could not fetch existing emails from database: {e}")
            return set()
        finally:
            if conn:
                conn.close()

    def save_leads_dataframe(self, leads_df: pd.DataFrame):
        """
        Saves new, scored leads from a DataFrame to the database, avoiding duplicates.
        
        Args:
            leads_df: A pandas DataFrame containing scored leads.
        """
        if leads_df.empty:
            logging.info("Received an empty DataFrame. No leads to save.")
            return

        existing_emails = self.get_existing_emails()
        
        # Filter out leads that are already in the database
        new_leads_df = leads_df[~leads_df['Email'].isin(existing_emails)].copy()

        if new_leads_df.empty:
            logging.info("No new leads to save to the database.")
            return

        # --- Prepare DataFrame for Database Schema ---

        # 1. Create the 'Opportunities' string from boolean columns
        def create_opportunities_string(row):
            opps = []
            if row.get('NeedsRedesign'):
                opps.append('Website Redesign')
            if row.get('NeedsReviews'):
                opps.append('Review Campaign')
            # Add more opportunity checks here in the future
            return ', '.join(opps)

        new_leads_df['Opportunities'] = new_leads_df.apply(create_opportunities_string, axis=1)

        # 2. Select and rename columns to match the database table
        db_columns = {
            'BusinessName': 'BusinessName',
            'Email': 'Email',
            'Phone': 'Phone',
            'Website': 'Website',
            'City': 'City',
            'TotalScore': 'TotalScore',
            'Tier': 'Tier',
            'EstimatedValue': 'EstimatedValue',
            'Opportunities': 'Opportunities'
        }
        
        # Ensure only columns that exist in the DataFrame are selected
        final_df = new_leads_df[[col for col in db_columns.keys() if col in new_leads_df.columns]]
        final_df = final_df.rename(columns=db_columns)

        # --- Save to Database ---
        try:
            conn = sqlite3.connect(self.db_path)
            # Use pandas.to_sql for efficient bulk insertion
            final_df.to_sql(
                'scored_leads', 
                conn, 
                if_exists='append', 
                index=False
            )
            logging.info(f"Successfully saved {len(final_df)} new leads to the database.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save leads to database: {e}")
        finally:
            if conn:
                conn.close()