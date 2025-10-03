"""Test script for the house price prediction API."""

import json
import requests
import pandas as pd
from pathlib import Path


def test_api():
    """Test the prediction API with sample data."""
    import os
    base_url = os.getenv('SERVICE_URL', 'http://localhost:8000')
    
    # Test health endpoint
    print("🔍 Testing health endpoint...")
    try:
        health_response = requests.get(f"{base_url}/health")
        health_response.raise_for_status()
        health_data = health_response.json()
        print(f"✅ Health check passed: {health_data}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Load test data
    test_data_path = Path("data/future_unseen_examples.csv")
    if not test_data_path.exists():
        print(f"❌ Test data not found: {test_data_path}")
        return
        
    df = pd.read_csv(test_data_path)
    print(f"📊 Loaded {len(df)} test examples")
    
    # Test prediction endpoint with first 5 examples
    print("\n🏠 Testing prediction endpoint...")
    for i in range(min(5, len(df))):
        row = df.iloc[i]
        
        # Convert to dict and ensure proper types
        house_data = {
            "bedrooms": int(row["bedrooms"]),
            "bathrooms": float(row["bathrooms"]),
            "sqft_living": int(row["sqft_living"]),
            "sqft_lot": int(row["sqft_lot"]),
            "floors": float(row["floors"]),
            "waterfront": int(row["waterfront"]),
            "view": int(row["view"]),
            "condition": int(row["condition"]),
            "grade": int(row["grade"]),
            "sqft_above": int(row["sqft_above"]),
            "sqft_basement": int(row["sqft_basement"]),
            "yr_built": int(row["yr_built"]),
            "yr_renovated": int(row["yr_renovated"]),
            "zipcode": str(row["zipcode"]),
            "lat": float(row["lat"]),
            "long": float(row["long"]),
            "sqft_living15": int(row["sqft_living15"]),
            "sqft_lot15": int(row["sqft_lot15"])
        }
        
        try:
            response = requests.post(
                f"{base_url}/predict",
                json=house_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            prediction_data = response.json()
            print(f"✅ Example {i+1}: Predicted price = ${prediction_data['prediction']:,.0f} "
                  f"(inference: {prediction_data['inference_ms']}ms)")
            
            if prediction_data.get('warnings'):
                print(f"   ⚠️  Warnings: {prediction_data['warnings']}")
                
        except Exception as e:
            print(f"❌ Example {i+1} failed: {e}")
    
    print(f"\n🎉 API testing completed!")


if __name__ == "__main__":
    test_api()

