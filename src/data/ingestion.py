# lead_scoring_system/src/data/ingestion.py
import pandas as pd
import os
import logging

class DataIngestion:
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans and standardizes DataFrame column names.
        - Converts to lowercase
        - Strips leading/trailing whitespace
        - Replaces spaces and special characters with underscores
        """
        clean_cols = {}
        for col in df.columns:
            # First, handle potential non-string column names
            col_str = str(col)
            # Apply cleaning steps
            new_col = col_str.strip().lower().replace(' ', '_').replace('-', '_')
            clean_cols[col] = new_col
        
        df = df.rename(columns=clean_cols)
        logging.info(f"Cleaned column names to: {list(df.columns)}")
        return df

    def load_gym_data(self, file_path: str) -> pd.DataFrame:
        """
        Load gym data from an Excel file, specifying the header row and cleaning column names.
        """
        try:
            # --- CRITICAL FIX HERE ---
            # header=1 tells pandas to use the SECOND row as the column headers (since it's 0-indexed).
            df = pd.read_excel(file_path, header=1)
            # --- END OF CRITICAL FIX ---
            
            # Apply the column cleaning function for consistency
            df = self._clean_column_names(df)
            return df
        except Exception as e:
            logging.error(f"Failed to load {file_path}: {e}")
            return pd.DataFrame()
    
    def batch_load_files(self, file_paths: list[str]) -> pd.DataFrame:
        """Load multiple Excel files, clean columns for each, and combine them."""
        combined_df = pd.DataFrame()
        for file_path in file_paths:
            df = self.load_gym_data(file_path)
            if not df.empty:
                df['source_file'] = os.path.basename(file_path)
                combined_df = pd.concat([combined_df, df], ignore_index=True)
        return combined_df