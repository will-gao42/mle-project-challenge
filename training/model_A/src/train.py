"""Training script for Model A (basic KNN model)."""

import json
import pathlib
import pickle
from datetime import datetime
from typing import List, Tuple

import pandas as pd
import numpy as np
import yaml
from sklearn import model_selection
from sklearn import neighbors
from sklearn import pipeline
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score


def load_config(config_path: str = "configs/params.yaml") -> dict:
    """Load training configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_data(
    sales_path: str, demographics_path: str, sales_column_selection: List[str]
) -> Tuple[pd.DataFrame, pd.Series]:
    """Load the target and feature data by merging sales and demographics.

    Args:
        sales_path: path to CSV file with home sale data
        demographics_path: path to CSV file with demographics data
        sales_column_selection: list of columns from sales data to be used as features

    Returns:
        Tuple containing two elements: a DataFrame and a Series of the same
        length. The DataFrame contains features for machine learning, the
        series contains the target variable (home sale price).
    """
    # Load sales data
    data = pd.read_csv(sales_path,
                       usecols=sales_column_selection,
                       dtype={'zipcode': str})
    
    # Load demographics data
    demographics = pd.read_csv(demographics_path,
                               dtype={'zipcode': str})

    # Merge data
    merged_data = data.merge(demographics, how="left",
                             on="zipcode").drop(columns="zipcode")
    
    # Remove the target variable from the dataframe, features will remain
    y = merged_data.pop('price')
    x = merged_data

    return x, y


def train_model(x_train: pd.DataFrame, y_train: pd.Series) -> pipeline.Pipeline:
    """Train the KNN model with preprocessing pipeline."""
    model = pipeline.make_pipeline(
        preprocessing.RobustScaler(),
        neighbors.KNeighborsRegressor()
    ).fit(x_train, y_train)
    
    return model


def evaluate_model(model: pipeline.Pipeline, x_test: pd.DataFrame, y_test: pd.Series, x_train: pd.DataFrame, y_train: pd.Series) -> dict:
    """Evaluate model performance with test set and cross-validation."""
    print("🔍 Evaluating model performance...")
    
    # Test set evaluation
    y_pred = model.predict(x_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    test_r2 = r2_score(y_test, y_pred)
    
    # Cross-validation for generalization assessment
    cv_scores = cross_val_score(model, x_train, y_train, cv=5, scoring='neg_mean_squared_error')
    cv_rmse = np.sqrt(-cv_scores)
    
    performance = {
        'test_rmse': float(test_rmse),
        'test_r2': float(test_r2),
        'cv_rmse_mean': float(cv_rmse.mean()),
        'cv_rmse_std': float(cv_rmse.std())
    }
    
    print(f"    Test RMSE: ${test_rmse:,.0f}, R²: {test_r2:.3f}")
    print(f"    CV RMSE: ${cv_rmse.mean():,.0f} ± ${cv_rmse.std():,.0f}")
    
    return performance


def save_artifacts(
    model: pipeline.Pipeline,
    features: List[str],
    output_dir: str,
    config: dict,
    performance: dict = None
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
        "algorithm": "KNeighborsRegressor",
        "preprocessing": "RobustScaler",
        "feature_count": len(features),
        "features": features,
        "training_timestamp": datetime.now().isoformat(),
        "config": config
    }
    
    # Add performance metrics if provided
    if performance:
        model_info["performance"] = performance
    
    with open(output_path / "model_info.json", 'w') as f:
        json.dump(model_info, f, indent=2)


def main():
    """Load data, train model, evaluate performance, and export artifacts."""
    print("🚀 Creating basic KNN model with validation...")
    
    # Load configuration
    config = load_config()
    
    # Extract paths and parameters from config
    sales_path = config["data"]["sales_path"]
    demographics_path = config["data"]["demographics_path"]
    sales_column_selection = config["features"]["sales_columns"]
    output_dir = config["output"]["artifacts_dir"]
    
    print("Loading data...")
    x, y = load_data(sales_path, demographics_path, sales_column_selection)
    
    print("Splitting data...")
    x_train, x_test, y_train, y_test = model_selection.train_test_split(
        x, y, 
        test_size=config["training"]["test_size"],
        random_state=config["training"]["random_state"]
    )

    print("Training model...")
    model = train_model(x_train, y_train)
    
    # Evaluate model performance
    performance = evaluate_model(model, x_test, y_test, x_train, y_train)
    
    print(f"\n🏆 Model Performance Summary:")
    print(f"   Test RMSE: ${performance['test_rmse']:,.0f}")
    print(f"   Test R²: {performance['test_r2']:.3f}")
    print(f"   CV RMSE: ${performance['cv_rmse_mean']:,.0f} ± ${performance['cv_rmse_std']:,.0f}")

    print("Saving artifacts...")
    save_artifacts(model, list(x_train.columns), output_dir, config, performance)
    
    print(f"✅ Model training completed. Artifacts saved to {output_dir}")
    print(f"   Algorithm: KNeighborsRegressor")
    print(f"   Features: {len(x_train.columns)}")
    print(f"   Performance: R² = {performance['test_r2']:.3f}")


if __name__ == "__main__":
    main()
