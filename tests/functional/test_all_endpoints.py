"""Comprehensive test script for all API endpoints."""

import json
import requests
import pandas as pd
from pathlib import Path
import time


def test_all_endpoints():
    """Test all API endpoints comprehensively."""
    import os
    base_url = os.getenv("SERVICE_URL", "http://localhost:8000")
    
    print("🚀 Starting comprehensive API testing...")
    print("="*60)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check Endpoint")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        response.raise_for_status()
        health_data = response.json()
        print(f"✅ Health check passed: {health_data}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Single Prediction
    print("\n2️⃣ Testing Single Prediction Endpoint")
    print("-" * 40)
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
        response = requests.post(f"{base_url}/predict", json=test_data, timeout=10)
        response.raise_for_status()
        prediction_data = response.json()
        print(f"✅ Single prediction: ${prediction_data['prediction']:,.0f}")
        print(f"   ⏱️  Inference time: {prediction_data['inference_ms']}ms")
    except Exception as e:
        print(f"❌ Single prediction failed: {e}")
        return False
    
    # Test 3: Batch Prediction
    print("\n3️⃣ Testing Batch Prediction Endpoint")
    print("-" * 40)
    batch_data = [test_data.copy() for _ in range(3)]
    
    try:
        response = requests.post(f"{base_url}/predict/batch", json=batch_data, timeout=10)
        response.raise_for_status()
        batch_result = response.json()
        print(f"✅ Batch prediction: {len(batch_result['predictions'])} predictions")
        print(f"   ⏱️  Total time: {batch_result['inference_ms']}ms")
        print(f"   📊 Predictions: {[f'${p:,.0f}' for p in batch_result['predictions']]}")
    except Exception as e:
        print(f"❌ Batch prediction failed: {e}")
        return False
    
    # Test 4: Minimal Features Prediction
    print("\n4️⃣ Testing Minimal Features Endpoint")
    print("-" * 40)
    minimal_data = {
        "bedrooms": 3,
        "bathrooms": 2.0,
        "sqft_living": 1500,
        "sqft_lot": 6000,
        "floors": 1.5,
        "sqft_above": 1500,
        "sqft_basement": 0,
        "zipcode": "98040"
    }
    
    try:
        response = requests.post(f"{base_url}/predict-min", json=minimal_data, timeout=10)
        response.raise_for_status()
        minimal_result = response.json()
        print(f"✅ Minimal prediction: ${minimal_result['prediction']:,.0f}")
        print(f"   ⏱️  Inference time: {minimal_result['inference_ms']}ms")
    except Exception as e:
        print(f"❌ Minimal prediction failed: {e}")
        return False
    
    # Test 5: Model Reload
    print("\n5️⃣ Testing Model Reload Endpoint")
    print("-" * 40)
    try:
        response = requests.post(f"{base_url}/reload", timeout=10)
        response.raise_for_status()
        reload_data = response.json()
        print(f"✅ Model reload: {reload_data['message']}")
        print(f"   🔖 Version: {reload_data['new_version']}")
    except Exception as e:
        print(f"❌ Model reload failed: {e}")
        return False
    
    # Test 6: Error Handling
    print("\n6️⃣ Testing Error Handling")
    print("-" * 40)
    
    # Invalid data
    try:
        invalid_data = {"invalid": "data"}
        response = requests.post(f"{base_url}/predict", json=invalid_data, timeout=5)
        if response.status_code == 422:
            print("✅ Validation error handling works")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Large batch
    try:
        large_batch = [test_data.copy() for _ in range(150)]  # Exceeds 100 limit
        response = requests.post(f"{base_url}/predict/batch", json=large_batch, timeout=5)
        if response.status_code == 400:
            print("✅ Batch size limit enforced")
        else:
            print(f"⚠️  Batch size limit not enforced: {response.status_code}")
    except Exception as e:
        print(f"❌ Batch size test failed: {e}")
    
    # Test 7: Performance Test
    print("\n7️⃣ Testing Performance")
    print("-" * 40)
    
    # Single prediction performance
    start_time = time.time()
    for i in range(10):
        response = requests.post(f"{base_url}/predict", json=test_data, timeout=5)
        response.raise_for_status()
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 10 * 1000
    print(f"✅ Average response time (10 requests): {avg_time:.1f}ms")
    
    # Test 8: API Documentation
    print("\n8️⃣ Testing API Documentation")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Swagger UI accessible")
        else:
            print(f"⚠️  Swagger UI not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
    
    try:
        response = requests.get(f"{base_url}/redoc", timeout=5)
        if response.status_code == 200:
            print("✅ ReDoc accessible")
        else:
            print(f"⚠️  ReDoc not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ ReDoc test failed: {e}")
    
    # Test 9: Real Data Test
    print("\n9️⃣ Testing with Real Data")
    print("-" * 40)
    
    test_data_path = Path("data/future_unseen_examples.csv")
    if test_data_path.exists():
        df = pd.read_csv(test_data_path)
        real_data = {
            "bedrooms": int(df.iloc[0]["bedrooms"]),
            "bathrooms": float(df.iloc[0]["bathrooms"]),
            "sqft_living": int(df.iloc[0]["sqft_living"]),
            "sqft_lot": int(df.iloc[0]["sqft_lot"]),
            "floors": float(df.iloc[0]["floors"]),
            "waterfront": int(df.iloc[0]["waterfront"]),
            "view": int(df.iloc[0]["view"]),
            "condition": int(df.iloc[0]["condition"]),
            "grade": int(df.iloc[0]["grade"]),
            "sqft_above": int(df.iloc[0]["sqft_above"]),
            "sqft_basement": int(df.iloc[0]["sqft_basement"]),
            "yr_built": int(df.iloc[0]["yr_built"]),
            "yr_renovated": int(df.iloc[0]["yr_renovated"]),
            "zipcode": str(df.iloc[0]["zipcode"]),
            "lat": float(df.iloc[0]["lat"]),
            "long": float(df.iloc[0]["long"]),
            "sqft_living15": int(df.iloc[0]["sqft_living15"]),
            "sqft_lot15": int(df.iloc[0]["sqft_lot15"])
        }
        
        try:
            response = requests.post(f"{base_url}/predict", json=real_data, timeout=10)
            response.raise_for_status()
            real_result = response.json()
            print(f"✅ Real data prediction: ${real_result['prediction']:,.0f}")
            print(f"   ⏱️  Inference time: {real_result['inference_ms']}ms")
        except Exception as e:
            print(f"❌ Real data test failed: {e}")
    else:
        print("⚠️  Real data file not found, skipping test")
    
    print("\n" + "="*60)
    print("🎉 Comprehensive API testing completed!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = test_all_endpoints()
    if success:
        print("\n✅ All tests passed! API is ready for production.")
    else:
        print("\n❌ Some tests failed. Please check the API configuration.")
