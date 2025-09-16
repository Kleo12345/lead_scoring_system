# lead_scoring_system/src/utils/db_manager.py
import sqlite3
import pandas as pd
import logging
from typing import Set

class DatabaseManager:
    def __init__(self, db_path: str = "leads.db"):
        """
        Initialize the DatabaseManager with a path to the SQLite file and ensure the database schema exists.
        
        Parameters:
            db_path (str): Filesystem path to the SQLite database file (defaults to "leads.db"). If the file does not exist, the database and the required scored_leads table will be created.
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """
        Ensure the scored_leads table exists and matches the expected schema.
        
        Creates the scored_leads table if it does not already exist with the following columns:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - BusinessName: TEXT NOT NULL
        - Email: TEXT NOT NULL UNIQUE
        - Phone: TEXT
        - Website: TEXT
        - City: TEXT
        - TotalScore: INTEGER
        - Tier: TEXT
        - EstimatedValue: TEXT
        - Opportunities: TEXT
        - CreatedDate: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        
        Side effects:
        - Opens a SQLite connection to self.db_path, creates the table if necessary, commits the change, and closes the connection.
        - Logs an error on sqlite3 failures but does not raise exceptions.
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
        """
        Return the set of unique Email values stored in the scored_leads table.
        
        Returns an empty set if the query fails (errors are logged). The database
        connection is always closed before returning.
        """
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
        Save new, scored leads from a pandas DataFrame into the database, skipping any rows whose Email already exists.
        
        Accepts a DataFrame of leads, deduplicates against the existing Email values in the database, derives an "Opportunities" comma-separated string from boolean flags (currently `NeedsRedesign` -> "Website Redesign" and `NeedsReviews` -> "Review Campaign"), aligns columns with the scored_leads table schema, and performs a bulk insert. If the DataFrame is empty or contains no new emails, the function returns without writing.
        
        Parameters:
            leads_df (pd.DataFrame): DataFrame of scored leads. Expected columns used by this method include:
                - Email (used for deduplication; required)
                - Any of BusinessName, Phone, Website, City, TotalScore, Tier, EstimatedValue (optional; only present columns are written)
                - NeedsRedesign, NeedsReviews (optional boolean flags used to build the Opportunities column)
        
        Side effects:
            Inserts rows into the `scored_leads` table in the configured SQLite database (self.db_path). Errors during insertion are logged; exceptions are not propagated by this function.
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
            """
            Build a comma-separated Opportunities string from boolean flags in a row.
            
            Parameters:
                row (Mapping): A dict-like or pandas.Series containing opportunity flags. Recognized keys:
                    - 'NeedsRedesign': if truthy, includes "Website Redesign".
                    - 'NeedsReviews': if truthy, includes "Review Campaign".
            
            Returns:
                str: A comma-and-space-separated list of opportunity names (empty string if none).
            """
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