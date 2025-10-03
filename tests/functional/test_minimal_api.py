"""Test script for the minimal features prediction API endpoint."""

import json
import requests
import pandas as pd
from pathlib import Path


def test_minimal_api():
    """Test the minimal features prediction API with sample data."""
    import os
    base_url = os.getenv("SERVICE_URL", "http://localhost:8000")
    
    # Test health endpoint first
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
    
    # Test minimal features endpoint with first 3 examples
    print("\n🏠 Testing minimal features prediction endpoint...")
    
    for i in range(min(3, len(df))):
        row = df.iloc[i]
        
        # Create minimal features (only the 8 core features)
        minimal_data = {
            "bedrooms": int(row["bedrooms"]),
            "bathrooms": float(row["bathrooms"]),
            "sqft_living": int(row["sqft_living"]),
            "sqft_lot": int(row["sqft_lot"]),
            "floors": float(row["floors"]),
            "sqft_above": int(row["sqft_above"]),
            "sqft_basement": int(row["sqft_basement"]),
            "zipcode": str(row["zipcode"])
        }
        
        try:
            response = requests.post(
                f"{base_url}/predict-min",
                json=minimal_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            prediction_data = response.json()
            print(f"✅ Example {i+1}: Predicted price = ${prediction_data['prediction']:,.0f} "
                  f"(inference: {prediction_data['inference_ms']}ms)")
            print(f"   📝 Minimal features: {minimal_data}")
            
            if prediction_data.get('warnings'):
                print(f"   ⚠️  Warnings: {prediction_data['warnings']}")
                
        except Exception as e:
            print(f"❌ Example {i+1} failed: {e}")
    
    # Test with edge case - very minimal data
    print("\n🧪 Testing with edge case data...")
    edge_case_data = {
        "bedrooms": 2,
        "bathrooms": 1.0,
        "sqft_living": 1000,
        "sqft_lot": 5000,
        "floors": 1.0,
        "sqft_above": 1000,
        "sqft_basement": 0,
        "zipcode": "98040"  # Known zipcode with demographics
    }
    
    try:
        response = requests.post(
            f"{base_url}/predict-min",
            json=edge_case_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        edge_result = response.json()
        print(f"✅ Edge case prediction: ${edge_result['prediction']:,.0f}")
        print(f"   📝 Edge case features: {edge_case_data}")
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
    
    # Compare with full features endpoint
    print("\n🔄 Comparing minimal vs full features prediction...")
    
    # Get first example for comparison
    row = df.iloc[0]
    
    # Full features
    full_data = {
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
    
    # Minimal features (same core data)
    minimal_data = {
        "bedrooms": int(row["bedrooms"]),
        "bathrooms": float(row["bathrooms"]),
        "sqft_living": int(row["sqft_living"]),
        "sqft_lot": int(row["sqft_lot"]),
        "floors": float(row["floors"]),
        "sqft_above": int(row["sqft_above"]),
        "sqft_basement": int(row["sqft_basement"]),
        "zipcode": str(row["zipcode"])
    }
    
    try:
        # Full prediction
        full_response = requests.post(f"{base_url}/predict", json=full_data)
        full_result = full_response.json()
        
        # Minimal prediction
        minimal_response = requests.post(f"{base_url}/predict-min", json=minimal_data)
        minimal_result = minimal_response.json()
        
        diff = abs(full_result['prediction'] - minimal_result['prediction'])
        diff_pct = (diff / full_result['prediction']) * 100
        
        print(f"✅ Comparison results:")
        print(f"   📊 Full features prediction: ${full_result['prediction']:,.0f}")
        print(f"   📊 Minimal features prediction: ${minimal_result['prediction']:,.0f}")
        print(f"   📈 Difference: ${diff:,.0f} ({diff_pct:.1f}%)")
        
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
    
    print(f"\n🎉 Minimal features API testing completed!")


if __name__ == "__main__":
    test_minimal_api()
