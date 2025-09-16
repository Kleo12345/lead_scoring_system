# lead_scoring_system/src/data/ingestion.py
import pandas as pd
import os
import logging

class DataIngestion:
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize DataFrame column names to a consistent snake_case-like format.
        
        This function casts each column name to string, strips leading/trailing whitespace,
        converts to lowercase, and replaces spaces and hyphens with underscores. It returns
        a DataFrame with columns renamed according to this mapping. Non-string column names
        are converted to strings before cleaning.
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
        Load gym data from an Excel file, using the second row as column headers, and normalize column names.
        
        Reads the Excel file at `file_path` with pandas using header=1 (treating the second row as the header), then applies _clean_column_names to produce normalized, lowercase, underscore-separated column names. If reading or cleaning fails, the method logs an error and returns an empty DataFrame.
        
        Parameters:
            file_path (str): Path to the Excel file to load.
        
        Returns:
            pd.DataFrame: The cleaned DataFrame loaded from the file, or an empty DataFrame on failure.
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
        """
        Load multiple Excel files, clean each with load_gym_data, and concatenate results.
        
        Each file in file_paths is read via load_gym_data; dataframes that are empty (e.g., on read error) are skipped.
        A new column, `source_file`, is added to each row containing the basename of the originating file.
        The order of rows follows the order of file_paths and their internal row order.
        
        Parameters:
            file_paths (list[str]): Iterable of filesystem paths to Excel files.
        
        Returns:
            pandas.DataFrame: Concatenated dataframe of all successfully loaded files. Returns an empty DataFrame if none loaded.
        """
        combined_df = pd.DataFrame()
        for file_path in file_paths:
            df = self.load_gym_data(file_path)
            if not df.empty:
                df['source_file'] = os.path.basename(file_path)
                combined_df = pd.concat([combined_df, df], ignore_index=True)
        return combined_df