"""Demographics data loading and lookup utilities."""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional


class DemographicsLoader:
    """Handles loading and lookup of demographics data by zipcode."""
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize with optional data path for flexibility."""
        self.data_path = data_path
        self.demographics_df: pd.DataFrame = None
        
    def load_demographics(self) -> None:
        """Load demographics data from CSV."""
        if self.data_path is None:
            raise ValueError("Data path not set. Provide data_path in constructor or set it directly.")
            
        demographics_path = Path(self.data_path)
        
        if not demographics_path.exists():
            raise FileNotFoundError(f"Demographics file not found: {demographics_path}")
            
        self.demographics_df = pd.read_csv(demographics_path)
        
        # Ensure zipcode is string for consistent lookup
        self.demographics_df['zipcode'] = self.demographics_df['zipcode'].astype(str)
        
    def get_demographics_by_zipcode(self, zipcode: str) -> Optional[Dict]:
        """Get demographics data for a specific zipcode."""
        if self.demographics_df is None:
            raise ValueError("Demographics not loaded. Call load_demographics() first.")
            
        # Convert zipcode to string for lookup (handle float zipcodes)
        zipcode_str = str(zipcode).replace('.0', '')
        
        # Find matching row
        match = self.demographics_df[self.demographics_df['zipcode'] == zipcode_str]
        
        if match.empty:
            return None
            
        # Return first match as dictionary (excluding zipcode column)
        row = match.iloc[0]
        demographics = row.drop('zipcode').to_dict()
        
        return demographics
        
    def enrich_with_demographics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich DataFrame with demographics data by zipcode."""
        if self.demographics_df is None:
            raise ValueError("Demographics not loaded. Call load_demographics() first.")
            
        # Ensure zipcode is string in input DataFrame (handle float zipcodes)
        df_copy = df.copy()
        df_copy['zipcode'] = df_copy['zipcode'].astype(str).str.replace('.0', '', regex=False)
        
        # Merge with demographics data
        enriched_df = df_copy.merge(
            self.demographics_df, 
            on='zipcode', 
            how='left'
        )
        
        return enriched_df
