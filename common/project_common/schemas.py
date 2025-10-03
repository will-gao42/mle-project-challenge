"""Pydantic schemas for API request/response models."""

from typing import List, Optional, Union
from pydantic import BaseModel, Field


class HouseFeatures(BaseModel):
    """Schema for house features from future_unseen_examples.csv."""
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=0, description="Number of bathrooms")
    sqft_living: int = Field(..., gt=0, description="Square feet of living space")
    sqft_lot: int = Field(..., gt=0, description="Square feet of lot")
    floors: float = Field(..., gt=0, description="Number of floors")
    waterfront: int = Field(..., ge=0, le=1, description="Waterfront property (0 or 1)")
    view: int = Field(..., ge=0, le=4, description="View rating (0-4)")
    condition: int = Field(..., ge=1, le=5, description="Condition rating (1-5)")
    grade: int = Field(..., ge=1, le=13, description="Grade rating (1-13)")
    sqft_above: int = Field(..., ge=0, description="Square feet above ground")
    sqft_basement: int = Field(..., ge=0, description="Square feet of basement")
    yr_built: int = Field(..., ge=1800, le=2024, description="Year built")
    yr_renovated: int = Field(..., ge=0, le=2024, description="Year renovated (0 if never)")
    zipcode: str = Field(..., description="ZIP code")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    long: float = Field(..., ge=-180, le=180, description="Longitude")
    sqft_living15: int = Field(..., gt=0, description="Living space of 15 nearest neighbors")
    sqft_lot15: int = Field(..., gt=0, description="Lot size of 15 nearest neighbors")


class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    prediction: float = Field(..., description="Predicted house price")
    model_version: str = Field(..., description="Model version hash")
    inference_ms: float = Field(..., description="Inference time in milliseconds")
    warnings: Optional[List[str]] = Field(default=None, description="Any warnings")


class BatchPredictionResponse(BaseModel):
    """Schema for batch prediction response."""
    predictions: List[float] = Field(..., description="List of predicted house prices")
    model_version: str = Field(..., description="Model version hash")
    inference_ms: float = Field(..., description="Total inference time in milliseconds")
    warnings: Optional[List[str]] = Field(default=None, description="Any warnings")
    count: int = Field(..., description="Number of predictions made")


class MinimalHouseFeatures(BaseModel):
    """Schema for minimal house features (only the 8 core features used by the model).
    
    Note: The model only uses these 8 features + demographics data.
    Additional features like waterfront, view, condition, etc. are provided
    as defaults for API compatibility but are NOT used in the actual prediction.
    """
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=0, description="Number of bathrooms")
    sqft_living: int = Field(..., gt=0, description="Square feet of living space")
    sqft_lot: int = Field(..., gt=0, description="Square feet of lot")
    floors: float = Field(..., gt=0, description="Number of floors")
    sqft_above: int = Field(..., ge=0, description="Square feet above ground")
    sqft_basement: int = Field(..., ge=0, description="Square feet of basement")
    zipcode: str = Field(..., description="ZIP code")


class ReloadRequest(BaseModel):
    """Schema for model reload request."""
    model_key: Optional[str] = Field(default=None, description="Model key (e.g., 'model_A', 'model_B')")
    model_dir: Optional[str] = Field(default=None, description="Direct model directory path")


class ReloadResponse(BaseModel):
    """Schema for model reload response."""
    status: str = Field(..., description="Reload status")
    old_version: str = Field(..., description="Previous model version")
    new_version: str = Field(..., description="New model version")
    message: str = Field(..., description="Reload message")


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(..., description="Service status")
    model_version: str = Field(..., description="Model version hash")
