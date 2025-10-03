"""Prediction logic with feature assembly and demographics enrichment."""

import time
from typing import List, Optional

import pandas as pd

from .demographics import DemographicsLoader
from .model_loader import ModelLoader


class Predictor:
    """Handles feature assembly, enrichment, and prediction."""
    
    def __init__(self, model_loader: ModelLoader, demographics_loader: DemographicsLoader):
        self.model_loader = model_loader
        self.demographics_loader = demographics_loader
        
    def predict_single(self, house_features: dict) -> dict:
        """Predict price for a single house with enrichment."""
        # Convert to DataFrame
        df = pd.DataFrame([house_features])
        
        # Enrich with demographics
        enriched_df = self.demographics_loader.enrich_with_demographics(df)
        
        # Check for missing demographics
        warnings = []
        if enriched_df.isnull().any().any():
            missing_cols = enriched_df.columns[enriched_df.isnull().any()].tolist()
            warnings.append(f"Missing demographics data for zipcode {house_features['zipcode']}: {missing_cols}")
        
        # Align features to model requirements
        feature_df = self._align_features(enriched_df)
        
        # Make prediction
        start_time = time.time()
        prediction = self.model_loader.predict(feature_df)
        inference_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "prediction": float(prediction[0]),
            "model_version": self.model_loader.get_model_version(),
            "inference_ms": round(inference_time, 2),
            "warnings": warnings if warnings else None
        }
        
    def predict_batch(self, house_features_list: List[dict]) -> dict:
        """Predict prices for multiple houses with enrichment."""
        if not house_features_list:
            return {
                "predictions": [],
                "model_version": self.model_loader.get_model_version(),
                "inference_ms": 0.0,
                "warnings": None,
                "count": 0
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(house_features_list)
        
        # Enrich with demographics
        enriched_df = self.demographics_loader.enrich_with_demographics(df)
        
        # Check for missing demographics
        warnings = []
        if enriched_df.isnull().any().any():
            missing_zipcodes = enriched_df[enriched_df.isnull().any(axis=1)]['zipcode'].unique().tolist()
            warnings.append(f"Missing demographics data for zipcodes: {missing_zipcodes}")
        
        # Align features to model requirements
        feature_df = self._align_features(enriched_df)
        
        # Make predictions
        start_time = time.time()
        predictions = self.model_loader.predict(feature_df)
        inference_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "predictions": [float(p) for p in predictions],
            "model_version": self.model_loader.get_model_version(),
            "inference_ms": round(inference_time, 2),
            "warnings": warnings if warnings else None,
            "count": len(predictions)
        }
        
    def predict_minimal(self, minimal_features: dict) -> dict:
        """Predict price using only minimal required features with smart defaults."""
        # Create full feature set with defaults
        full_features = self._expand_minimal_features(minimal_features)
        
        # Use the single prediction method
        return self.predict_single(full_features)
        
    def _expand_minimal_features(self, minimal_features: dict) -> dict:
        """Expand minimal features to full feature set with smart defaults.
        
        Note: The model only uses 8 core house features + demographics.
        The additional features (waterfront, view, condition, etc.) are provided
        for API compatibility but are NOT used by the model.
        """
        # Start with minimal features (the 8 core features the model actually uses)
        full_features = minimal_features.copy()
        
        # Add defaults for API compatibility (these are NOT used by the model)
        # These are only needed to match the full API schema
        api_defaults = {
            "waterfront": 0,  # Most houses are not waterfront
            "view": 0,        # Most houses have no special view
            "condition": 3,   # Average condition
            "grade": 7,       # Average grade
            "yr_built": 2000, # Reasonable default year
            "yr_renovated": 0, # Most houses not renovated
            "lat": 47.6,      # Seattle area latitude
            "long": -122.3,   # Seattle area longitude
            "sqft_living15": minimal_features.get("sqft_living", 2000),  # Use same as sqft_living
            "sqft_lot15": minimal_features.get("sqft_lot", 8000)         # Use same as sqft_lot
        }
        
        # Add defaults for any missing API features
        for key, default_value in api_defaults.items():
            if key not in full_features:
                full_features[key] = default_value
                
        return full_features
        
    def _align_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Align DataFrame columns to model feature requirements."""
        required_features = self.model_loader.features
        
        # Select only the required features in the correct order
        feature_df = df[required_features].copy()
        
        # Fill any missing values with 0 (simple fallback)
        feature_df = feature_df.fillna(0)
        
        return feature_df

