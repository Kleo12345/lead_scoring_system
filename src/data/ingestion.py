# lead_scoring_system/src/data/ingestion.py
import pandas as pd
import os
from typing import List, Dict
import logging

class DataIngestion:
    def load_gym_data(self, file_path: str) -> pd.DataFrame:
        """Load gym data from Excel files"""
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            logging.error(f"Failed to load {file_path}: {e}")
            return pd.DataFrame()
    
    def batch_load_files(self, file_paths: List[str]) -> pd.DataFrame:
        """Load multiple Excel files and combine"""
        combined_df = pd.DataFrame()
        for file_path in file_paths:
            df = self.load_gym_data(file_path)
            if not df.empty:
                df['source_file'] = os.path.basename(file_path)
                combined_df = pd.concat([combined_df, df], ignore_index=True)
        return combined_df
