"""FastAPI application for house price prediction."""

from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .model_loader import ModelLoader
from .predictor import Predictor
from .demographics import DemographicsLoader
from .schemas import (
    HouseFeatures, PredictionResponse, BatchPredictionResponse, 
    MinimalHouseFeatures, ReloadRequest, ReloadResponse, HealthResponse
)
from .filesystem_registry import resolve_model_key

# Initialize FastAPI app
app = FastAPI(
    title="House Price Prediction API",
    description="API for predicting house prices using machine learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global variables for loaded components
model_loader = None
demographics_loader = None
predictor = None


@app.on_event("startup")
async def startup_event():
    """Initialize model and demographics data on startup."""
    global model_loader, demographics_loader, predictor
    
    try:
        # Get model directory from environment
        import os
        from pathlib import Path
        
        model_base_dir = os.getenv("MODEL_BASE_DIR", "/models")
        default_model_key = os.getenv("DEFAULT_MODEL_KEY", "model_A")
        
        # Resolve model directory
        if default_model_key:
            model_dir = resolve_model_key(default_model_key, model_base_dir)
        else:
            model_dir = Path(os.getenv("MODEL_DIR", "model"))
        
        # Load model
        model_loader = ModelLoader(str(model_dir))
        model_loader.load_model()
        
        # Load demographics from resources
        demographics_path = str(Path(__file__).resolve().parents[1] / "resources" / "zipcode_demographics.csv")
        demographics_loader = DemographicsLoader(demographics_path)
        demographics_loader.load_demographics()
        
        # Initialize predictor
        predictor = Predictor(model_loader, demographics_loader)
        
        print(f"✅ Model loaded successfully (version: {model_loader.get_model_version()})")
        print(f"✅ Demographics loaded successfully ({len(demographics_loader.demographics_df)} zipcodes)")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if model_loader is None or model_loader.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if demographics_loader is None or demographics_loader.demographics_df is None:
        raise HTTPException(status_code=503, detail="Demographics not loaded")
        
    return HealthResponse(
        status="ok",
        model_version=model_loader.get_model_version()
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_price(house_features: HouseFeatures):
    """Predict house price for a single property."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    try:
        # Convert Pydantic model to dict
        features_dict = house_features.dict()
        
        # Make prediction
        result = predictor.predict_single(features_dict)
        
        return PredictionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch_prices(house_features_list: List[HouseFeatures]):
    """Predict house prices for multiple properties."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    if len(house_features_list) > 100:  # Reasonable batch size limit
        raise HTTPException(status_code=400, detail="Batch size too large. Maximum 100 records per request.")
    
    try:
        # Convert Pydantic models to dicts
        features_dicts = [features.dict() for features in house_features_list]
        
        # Make predictions
        result = predictor.predict_batch(features_dicts)
        
        return BatchPredictionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.post("/predict-min", response_model=PredictionResponse)
async def predict_price_minimal(minimal_features: MinimalHouseFeatures):
    """Predict house price using only minimal required features (bonus endpoint)."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    try:
        # Convert Pydantic model to dict
        features_dict = minimal_features.dict()
        
        # Make prediction with minimal features
        result = predictor.predict_minimal(features_dict)
        
        return PredictionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Minimal prediction failed: {str(e)}")


@app.post("/reload", response_model=ReloadResponse)
async def reload_model(req: ReloadRequest = None):
    """Reload model artifacts from disk (hot reload without restart).
    
    Supports switching between models via model_key or direct model_dir.
    """
    if model_loader is None:
        raise HTTPException(status_code=503, detail="Model loader not initialized")
    
    try:
        import os
        from pathlib import Path
        
        # Determine target model directory
        target_dir = None
        if req:
            if req.model_key:
                model_base_dir = os.getenv("MODEL_BASE_DIR", "/models")
                target_dir = resolve_model_key(req.model_key, model_base_dir)
            elif req.model_dir:
                target_dir = Path(req.model_dir)
        
        # Update model directory if specified
        if target_dir:
            model_loader.model_dir = Path(target_dir)
            print(f"🔄 Switching to model directory: {target_dir}")
        
        old_version = model_loader.get_model_version()
        new_version = model_loader.reload_model()
        
        # Reinitialize predictor with new model
        global predictor
        predictor = Predictor(model_loader, demographics_loader)
        
        message = "Model reloaded successfully"
        if old_version != new_version:
            message = f"Model updated from {old_version} to {new_version}"
        elif target_dir:
            message = f"Model switched to {target_dir.name}"
        
        return ReloadResponse(
            status="success",
            old_version=old_version,
            new_version=new_version,
            message=message
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model reload failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

