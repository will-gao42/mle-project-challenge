"""Model loading and versioning utilities."""

import hashlib
import json
import pickle
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from sklearn.base import BaseEstimator


class ModelLoader:
    """Handles loading and versioning of model artifacts."""
    
    def __init__(self, model_dir: str = "model"):
        self.model_dir = Path(model_dir)
        self.model: BaseEstimator = None
        self.features: List[str] = None
        self.model_version: str = None
        
    def load_model(self) -> None:
        """Load model and features from disk."""
        model_path = self.model_dir / "model.pkl"
        features_path = self.model_dir / "model_features.json"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not features_path.exists():
            raise FileNotFoundError(f"Features file not found: {features_path}")
            
        # Load model
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        # Load features
        with open(features_path, 'r') as f:
            self.features = json.load(f)
            
        # Compute model version from file hash
        self.model_version = self._compute_file_hash(model_path)
        
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of model file for versioning."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:16]  # Use first 16 chars for brevity
        
    def get_model_version(self) -> str:
        """Get current model version."""
        return self.model_version or "unknown"
        
    def predict(self, X: pd.DataFrame) -> Any:
        """Make predictions using the loaded model."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        return self.model.predict(X)
        
    def reload_model(self) -> str:
        """Reload model and features from disk, returning new version."""
        old_version = self.model_version
        
        try:
            # Check if model file has changed before reloading
            model_path = self.model_dir / "model.pkl"
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
                
            # Compute new version hash
            new_version = self._compute_file_hash(model_path)
            
            if old_version == new_version:
                print(f"🔄 Model unchanged (version: {new_version})")
                return new_version
            
            # Model has changed, reload it
            print(f"🔄 Model changed: {old_version} → {new_version}")
            self.load_model()
            
            return new_version
            
        except Exception as e:
            print(f"❌ Model reload failed: {e}")
            raise

