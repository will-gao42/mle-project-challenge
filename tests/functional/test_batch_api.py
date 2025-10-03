"""Test script for the batch prediction API endpoint."""

import json
import requests
import pandas as pd
from pathlib import Path


def test_batch_api():
    """Test the batch prediction API with sample data."""
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
    
    # Test batch prediction endpoint with first 5 examples
    print("\n🏠 Testing batch prediction endpoint...")
    
    # Prepare batch data
    batch_data = []
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
        batch_data.append(house_data)
    
    try:
        response = requests.post(
            f"{base_url}/predict/batch",
            json=batch_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        batch_result = response.json()
        print(f"✅ Batch prediction successful:")
        print(f"   📈 Predictions: {[f'${p:,.0f}' for p in batch_result['predictions']]}")
        print(f"   ⏱️  Total inference time: {batch_result['inference_ms']}ms")
        print(f"   📊 Count: {batch_result['count']}")
        print(f"   🔖 Model version: {batch_result['model_version']}")
        
        if batch_result.get('warnings'):
            print(f"   ⚠️  Warnings: {batch_result['warnings']}")
            
    except Exception as e:
        print(f"❌ Batch prediction failed: {e}")
    
    # Test empty batch
    print("\n🧪 Testing empty batch...")
    try:
        response = requests.post(
            f"{base_url}/predict/batch",
            json=[],
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        empty_result = response.json()
        print(f"✅ Empty batch handled correctly: {empty_result}")
        
    except Exception as e:
        print(f"❌ Empty batch test failed: {e}")
    
    # Test batch size limit
    print("\n🚫 Testing batch size limit...")
    try:
        large_batch = batch_data * 25  # 125 records (exceeds 100 limit)
        response = requests.post(
            f"{base_url}/predict/batch",
            json=large_batch,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print(f"✅ Batch size limit enforced: {response.json()}")
        else:
            print(f"❌ Batch size limit not enforced: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Batch size limit test failed: {e}")
    
    print(f"\n🎉 Batch API testing completed!")


if __name__ == "__main__":
    test_batch_api()
