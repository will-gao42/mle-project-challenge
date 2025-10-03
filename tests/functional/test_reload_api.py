"""Test script for the model reload API endpoint."""

import json
import requests
import time
from pathlib import Path


def test_reload_api():
    """Test the model reload API functionality."""
    import os
    base_url = os.getenv("SERVICE_URL", "http://localhost:8000")
    
    # Test health endpoint first
    print("🔍 Testing health endpoint...")
    try:
        health_response = requests.get(f"{base_url}/health")
        health_response.raise_for_status()
        health_data = health_response.json()
        print(f"✅ Health check passed: {health_data}")
        initial_version = health_data['model_version']
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test reload endpoint
    print("\n🔄 Testing model reload endpoint...")
    try:
        reload_response = requests.post(f"{base_url}/reload")
        reload_response.raise_for_status()
        
        reload_data = reload_response.json()
        print(f"✅ Model reload successful:")
        print(f"   📊 Status: {reload_data['status']}")
        print(f"   🔖 Old version: {reload_data['old_version']}")
        print(f"   🔖 New version: {reload_data['new_version']}")
        print(f"   💬 Message: {reload_data['message']}")
        
        # Verify health check still works after reload
        print("\n🔍 Verifying health check after reload...")
        health_response = requests.get(f"{base_url}/health")
        health_response.raise_for_status()
        health_data = health_response.json()
        print(f"✅ Health check after reload: {health_data}")
        
    except Exception as e:
        print(f"❌ Model reload failed: {e}")
        return
    
    # Test that predictions still work after reload
    print("\n🏠 Testing predictions after reload...")
    test_data = {
        "bedrooms": 3,
        "bathrooms": 2.0,
        "sqft_living": 1500,
        "sqft_lot": 6000,
        "floors": 1.5,
        "waterfront": 0,
        "view": 0,
        "condition": 3,
        "grade": 7,
        "sqft_above": 1500,
        "sqft_basement": 0,
        "yr_built": 2000,
        "yr_renovated": 0,
        "zipcode": "98040",
        "lat": 47.6,
        "long": -122.3,
        "sqft_living15": 1500,
        "sqft_lot15": 6000
    }
    
    try:
        prediction_response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        prediction_response.raise_for_status()
        
        prediction_data = prediction_response.json()
        print(f"✅ Prediction after reload: ${prediction_data['prediction']:,.0f}")
        print(f"   🔖 Model version: {prediction_data['model_version']}")
        
    except Exception as e:
        print(f"❌ Prediction after reload failed: {e}")
    
    # Test multiple reloads
    print("\n🔄 Testing multiple reloads...")
    for i in range(3):
        try:
            reload_response = requests.post(f"{base_url}/reload")
            reload_response.raise_for_status()
            
            reload_data = reload_response.json()
            print(f"✅ Reload {i+1}: {reload_data['message']}")
            
            # Small delay between reloads
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Reload {i+1} failed: {e}")
    
    print(f"\n🎉 Model reload API testing completed!")


if __name__ == "__main__":
    test_reload_api()
