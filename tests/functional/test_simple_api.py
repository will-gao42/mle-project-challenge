"""Simple test script for the house price prediction API (no pandas required)."""

import json
import requests
import os


def test_simple_api():
    """Test the prediction API with simple requests."""
    base_url = os.getenv('SERVICE_URL', 'http://localhost:8000')
    
    print("🧪 Testing API endpoints...")
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        health_response = requests.get(f"{base_url}/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        print(f"   ✅ Health check passed: {health_data['status']}")
        print(f"   Model version: {health_data['model_version']}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test prediction endpoint
    print("2. Testing prediction endpoint...")
    test_house = {
        "bedrooms": 3,
        "bathrooms": 2.5,
        "sqft_living": 2000,
        "sqft_lot": 8000,
        "floors": 2.0,
        "waterfront": 0,
        "view": 0,
        "condition": 3,
        "grade": 7,
        "sqft_above": 2000,
        "sqft_basement": 0,
        "yr_built": 2000,
        "yr_renovated": 0,
        "zipcode": "98101",
        "lat": 47.6,
        "long": -122.3,
        "sqft_living15": 2000,
        "sqft_lot15": 8000
    }
    
    try:
        pred_response = requests.post(f"{base_url}/predict", json=test_house)
        assert pred_response.status_code == 200
        pred_data = pred_response.json()
        print(f"   ✅ Prediction successful: ${pred_data['prediction']:,.0f}")
        print(f"   Model version: {pred_data['model_version']}")
        print(f"   Inference time: {pred_data['inference_ms']}ms")
    except Exception as e:
        print(f"   ❌ Prediction failed: {e}")
        return False
    
    # Test minimal prediction endpoint
    print("3. Testing minimal prediction endpoint...")
    minimal_house = {
        "bedrooms": 3,
        "bathrooms": 2.5,
        "sqft_living": 2000,
        "sqft_lot": 8000,
        "floors": 2.0,
        "sqft_above": 2000,
        "sqft_basement": 0,
        "zipcode": "98101"
    }
    
    try:
        min_pred_response = requests.post(f"{base_url}/predict-min", json=minimal_house)
        assert min_pred_response.status_code == 200
        min_pred_data = min_pred_response.json()
        print(f"   ✅ Minimal prediction successful: ${min_pred_data['prediction']:,.0f}")
    except Exception as e:
        print(f"   ❌ Minimal prediction failed: {e}")
        return False
    
    # Test reload endpoint
    print("4. Testing model reload...")
    try:
        reload_response = requests.post(f"{base_url}/reload")
        assert reload_response.status_code == 200
        reload_data = reload_response.json()
        print(f"   ✅ Reload successful: {reload_data['message']}")
    except Exception as e:
        print(f"   ❌ Reload failed: {e}")
        return False
    
    print("🎉 All tests passed!")
    return True


if __name__ == "__main__":
    success = test_simple_api()
    if not success:
        exit(1)
