"""Training script for Model B (improved model with multiple algorithms)."""

import json
import pathlib
import pickle
from datetime import datetime
from typing import List, Tuple, Dict

import pandas as pd
import numpy as np
import yaml
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline


def load_config(config_path: str = "configs/params.yaml") -> dict:
    """Load training configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_data(
    sales_path: str, demographics_path: str, sales_column_selection: List[str]
) -> Tuple[pd.DataFrame, pd.Series]:
    """Load and prepare the training data."""
    print("📊 Loading training data...")
    
    # Load house sales data
    data = pd.read_csv(sales_path, usecols=sales_column_selection, dtype={'zipcode': str})
    demographics = pd.read_csv(demographics_path, dtype={'zipcode': str})
    
    # Merge with demographics
    merged_data = data.merge(demographics, how="left", on="zipcode").drop(columns="zipcode")
    
    # Handle missing demographics with median imputation
    merged_data = merged_data.fillna(merged_data.median())
    
    # Separate features and target
    y = merged_data.pop('price')
    X = merged_data
    
    print(f"✅ Loaded {len(X)} samples with {len(X.columns)} features")
    return X, y


def evaluate_models(X: pd.DataFrame, y: pd.Series, config: dict) -> Dict:
    """Evaluate different traditional ML algorithms."""
    print("🔍 Evaluating different models...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=config["training"]["test_size"], 
        random_state=config["training"]["random_state"]
    )
    
    # Define models to test
    models = {
        'RandomForest': RandomForestRegressor(
            n_estimators=config["models"]["random_forest"]["n_estimators"], 
            random_state=config["training"]["random_state"], 
            n_jobs=-1
        ),
        'GradientBoosting': GradientBoostingRegressor(
            n_estimators=config["models"]["gradient_boosting"]["n_estimators"], 
            random_state=config["training"]["random_state"]
        ),
        'Ridge': Ridge(alpha=config["models"]["ridge"]["alpha"]),
        'Lasso': Lasso(alpha=config["models"]["lasso"]["alpha"]),
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"  Testing {name}...")
        
        # Create pipeline with scaling
        pipeline = Pipeline([
            ('scaler', RobustScaler()),
            ('regressor', model)
        ])
        
        # Fit and predict
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
        cv_rmse = np.sqrt(-cv_scores)
        
        results[name] = {
            'model': pipeline,
            'test_rmse': rmse,
            'test_r2': r2,
            'cv_rmse_mean': cv_rmse.mean(),
            'cv_rmse_std': cv_rmse.std()
        }
        
        print(f"    Test RMSE: ${rmse:,.0f}, R²: {r2:.3f}")
        print(f"    CV RMSE: ${cv_rmse.mean():,.0f} ± ${cv_rmse.std():,.0f}")
    
    return results


def save_artifacts(
    model: Pipeline,
    features: List[str],
    output_dir: str,
    config: dict,
    model_name: str,
    performance: dict
) -> None:
    """Save model artifacts and metadata."""
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Save model
    with open(output_path / "model.pkl", 'wb') as f:
        pickle.dump(model, f)
    
    # Save features
    with open(output_path / "model_features.json", 'w') as f:
        json.dump(features, f)
    
    # Save model info
    model_info = {
        "algorithm": model_name,
        "preprocessing": "RobustScaler",
        "feature_count": len(features),
        "features": features,
        "training_timestamp": datetime.now().isoformat(),
        "config": config,
        "performance": performance
    }
    
    with open(output_path / "model_info.json", 'w') as f:
        json.dump(model_info, f, indent=2)


def main():
    """Create and save an improved model."""
    print("🚀 Creating improved model...")
    
    # Load configuration
    config = load_config()
    
    # Extract paths and parameters from config
    sales_path = config["data"]["sales_path"]
    demographics_path = config["data"]["demographics_path"]
    sales_column_selection = config["features"]["sales_columns"]
    output_dir = config["output"]["artifacts_dir"]
    
    # Load data
    X, y = load_data(sales_path, demographics_path, sales_column_selection)
    
    # Evaluate models
    results = evaluate_models(X, y, config)
    
    # Select best model based on test R²
    best_model_name = max(results.keys(), key=lambda k: results[k]['test_r2'])
    best_model = results[best_model_name]['model']
    
    print(f"\n🏆 Best model: {best_model_name}")
    print(f"   Test RMSE: ${results[best_model_name]['test_rmse']:,.0f}")
    print(f"   Test R²: {results[best_model_name]['test_r2']:.3f}")
    
    # Train final model on full dataset
    print("\n🔄 Training final model on full dataset...")
    final_model = best_model
    final_model.fit(X, y)
    
    # Save artifacts
    print("Saving artifacts...")
    save_artifacts(
        final_model, 
        list(X.columns), 
        output_dir, 
        config,
        best_model_name,
        {
            'test_rmse': float(results[best_model_name]['test_rmse']),
            'test_r2': float(results[best_model_name]['test_r2']),
            'cv_rmse_mean': float(results[best_model_name]['cv_rmse_mean']),
            'cv_rmse_std': float(results[best_model_name]['cv_rmse_std'])
        }
    )
    
    print(f"✅ Improved model saved to {output_dir}/")
    print(f"   Algorithm: {best_model_name}")
    print(f"   Features: {len(X.columns)}")
    print(f"   Performance: R² = {results[best_model_name]['test_r2']:.3f}")


if __name__ == "__main__":
    main()
