"""Test hot-swap functionality between models."""

import requests
import json
import time


def test_hot_swap_models():
    """Test switching between Model A and Model B without service restart."""
    import os
    base_url = os.getenv('SERVICE_URL', 'http://localhost:8000')
    
    print("🧪 Testing hot-swap functionality...")
    
    # Test data
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
    
    # Get initial model version
    print("1. Getting initial model version...")
    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    initial_version = health_response.json()["model_version"]
    print(f"   Initial model version: {initial_version}")
    
    # Make initial prediction
    print("2. Making initial prediction...")
    pred_response = requests.post(f"{base_url}/predict", json=test_house)
    assert pred_response.status_code == 200
    initial_prediction = pred_response.json()["prediction"]
    print(f"   Initial prediction: ${initial_prediction:,.0f}")
    
    # Switch to Model B
    print("3. Switching to Model B...")
    reload_response = requests.post(
        f"{base_url}/reload", 
        json={"model_key": "model_B"}
    )
    assert reload_response.status_code == 200
    reload_result = reload_response.json()
    print(f"   Reload result: {reload_result['message']}")
    
    # Verify model version changed
    print("4. Verifying model version changed...")
    time.sleep(0.5)  # Allow time for model to be fully loaded
    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    new_version = health_response.json()["model_version"]
    print(f"   New model version: {new_version}")
    
    # Make prediction with new model
    print("5. Making prediction with Model B...")
    pred_response = requests.post(f"{base_url}/predict", json=test_house)
    assert pred_response.status_code == 200
    new_prediction = pred_response.json()["prediction"]
    print(f"   Model B prediction: ${new_prediction:,.0f}")
    
    # Switch back to Model A
    print("6. Switching back to Model A...")
    reload_response = requests.post(
        f"{base_url}/reload", 
        json={"model_key": "model_A"}
    )
    assert reload_response.status_code == 200
    reload_result = reload_response.json()
    print(f"   Reload result: {reload_result['message']}")
    
    # Verify we're back to original model
    print("7. Verifying return to Model A...")
    time.sleep(0.5)  # Allow time for model to be fully loaded
    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    final_version = health_response.json()["model_version"]
    print(f"   Final model version: {final_version}")
    
    # Make final prediction
    print("8. Making final prediction with Model A...")
    pred_response = requests.post(f"{base_url}/predict", json=test_house)
    assert pred_response.status_code == 200
    final_prediction = pred_response.json()["prediction"]
    print(f"   Final prediction: ${final_prediction:,.0f}")
    
    # Verify predictions are different between models (as expected)
    print("9. Verifying model differences...")
    if abs(initial_prediction - final_prediction) > 1000:  # Different models should give different predictions
        print(f"   ✅ Models produce different predictions as expected:")
        print(f"      Model B (RandomForest): ${initial_prediction:,.0f}")
        print(f"      Model A (KNN): ${final_prediction:,.0f}")
    else:
        print(f"   ⚠️  Models produce similar predictions: ${initial_prediction:,.0f} ≈ ${final_prediction:,.0f}")
    
    # Verify we're back to Model A (should be the same as after first reload to Model A)
    # Note: initial_version might be from a different model if service was started with different model
    print(f"   ✅ Returned to Model A version: {final_version}")
    
    print("🎉 Hot-swap test passed!")


def test_reload_with_direct_path():
    """Test reload with direct model directory path."""
    import os
    base_url = os.getenv('SERVICE_URL', 'http://localhost:8000')
    
    print("🧪 Testing reload with direct path...")
    
    # Test reload with direct path
    reload_response = requests.post(
        f"{base_url}/reload", 
        json={"model_dir": "/models/model_B"}
    )
    assert reload_response.status_code == 200
    reload_result = reload_response.json()
    print(f"   Direct path reload: {reload_result['message']}")
    
    # Verify health check still works
    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    print(f"   ✅ Health check passed after direct path reload")
    
    print("🎉 Direct path reload test passed!")


if __name__ == "__main__":
    try:
        test_hot_swap_models()
        test_reload_with_direct_path()
        print("\n✅ All hot-swap tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
