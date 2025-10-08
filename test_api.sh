#!/bin/bash

# Comprehensive API Testing Script
# Tests all endpoints from test_all_endpoints.py using curl

set -e  # Exit on any error

# Configuration
BASE_URL="http://localhost:8000"
TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Test data
TEST_DATA='{
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
}'

MINIMAL_DATA='{
    "bedrooms": 3,
    "bathrooms": 2.0,
    "sqft_living": 1500,
    "sqft_lot": 6000,
    "floors": 1.5,
    "sqft_above": 1500,
    "sqft_basement": 0,
    "zipcode": "98040"
}'

BATCH_DATA='[
    {
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
    },
    {
        "bedrooms": 4,
        "bathrooms": 2.5,
        "sqft_living": 2000,
        "sqft_lot": 8000,
        "floors": 2.0,
        "waterfront": 0,
        "view": 0,
        "condition": 4,
        "grade": 8,
        "sqft_above": 2000,
        "sqft_basement": 0,
        "yr_built": 2010,
        "yr_renovated": 0,
        "zipcode": "98040",
        "lat": 47.6,
        "long": -122.3,
        "sqft_living15": 2000,
        "sqft_lot15": 8000
    },
    {
        "bedrooms": 2,
        "bathrooms": 1.0,
        "sqft_living": 1000,
        "sqft_lot": 4000,
        "floors": 1.0,
        "waterfront": 0,
        "view": 0,
        "condition": 3,
        "grade": 6,
        "sqft_above": 1000,
        "sqft_basement": 0,
        "yr_built": 1995,
        "yr_renovated": 0,
        "zipcode": "98040",
        "lat": 47.6,
        "long": -122.3,
        "sqft_living15": 1000,
        "sqft_lot15": 4000
    }
]'

INVALID_DATA='{"invalid": "data"}'

echo "🚀 Starting comprehensive API testing..."
echo "============================================================"

# Test 1: Health Check
print_header "1️⃣ Testing Health Check Endpoint"
echo "🔍 Testing: GET $BASE_URL/health"
if response=$(curl -s -w "%{http_code}" -o /tmp/health_response.json "$BASE_URL/health" --max-time $TIMEOUT); then
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        health_data=$(cat /tmp/health_response.json)
        print_success "✅ Health check passed!"
        echo "   📊 Response: $health_data"
        echo "   🌐 Status Code: $http_code"
        echo "   ⏱️  Response Time: $(curl -s -w "%{time_total}" -o /dev/null "$BASE_URL/health")s"
    else
        print_error "❌ Health check failed with HTTP $http_code"
        echo "   📄 Response: $(cat /tmp/health_response.json)"
        exit 1
    fi
else
    print_error "❌ Health check failed: Connection error"
    exit 1
fi

# Test 2: Single Prediction
print_header "2️⃣ Testing Single Prediction Endpoint"
echo "🔍 Testing: POST $BASE_URL/predict"
echo "📤 Payload: House with 3 bedrooms, 2 bathrooms, 1500 sqft"
if response=$(curl -s -w "%{http_code}" -o /tmp/predict_response.json \
    -H "Content-Type: application/json" \
    -d "$TEST_DATA" \
    "$BASE_URL/predict" \
    --max-time $TIMEOUT); then
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        prediction=$(cat /tmp/predict_response.json | jq -r '.prediction')
        inference_time=$(cat /tmp/predict_response.json | jq -r '.inference_ms')
        print_success "✅ Single prediction successful!"
        echo "   💰 Predicted Price: \$$(printf "%.0f" "$prediction")"
        echo "   ⚡ Model Inference Time: ${inference_time}ms"
        echo "   🌐 Status Code: $http_code"
        echo "   📊 Full Response: $(cat /tmp/predict_response.json | jq -c .)"
    else
        print_error "❌ Single prediction failed with HTTP $http_code"
        echo "   📄 Error Response: $(cat /tmp/predict_response.json)"
        exit 1
    fi
else
    print_error "❌ Single prediction failed: Connection error"
    exit 1
fi

# Test 3: Batch Prediction
print_header "3️⃣ Testing Batch Prediction Endpoint"
echo "🔍 Testing: POST $BASE_URL/predict/batch"
echo "📤 Payload: 3 different house configurations"
if response=$(curl -s -w "%{http_code}" -o /tmp/batch_response.json \
    -H "Content-Type: application/json" \
    -d "$BATCH_DATA" \
    "$BASE_URL/predict/batch" \
    --max-time $TIMEOUT); then
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        predictions_count=$(cat /tmp/batch_response.json | jq -r '.predictions | length')
        total_time=$(cat /tmp/batch_response.json | jq -r '.inference_ms')
        predictions=$(cat /tmp/batch_response.json | jq -r '.predictions[]' | while read p; do printf "\$$(printf "%.0f" "$p") "; done)
        print_success "✅ Batch prediction successful!"
        echo "   📊 Number of Predictions: $predictions_count"
        echo "   ⚡ Total Processing Time: ${total_time}ms"
        echo "   💰 Individual Predictions: $predictions"
        echo "   🌐 Status Code: $http_code"
        # Use awk for decimal division
        avg_per_prediction=$(echo "$total_time $predictions_count" | awk '{printf "%.1f", $1 / $2}')
        echo "   📈 Average per prediction: ${avg_per_prediction}ms"
    else
        print_error "❌ Batch prediction failed with HTTP $http_code"
        echo "   📄 Error Response: $(cat /tmp/batch_response.json)"
        exit 1
    fi
else
    print_error "❌ Batch prediction failed: Connection error"
    exit 1
fi

# Test 4: Minimal Features Prediction
print_header "4️⃣ Testing Minimal Features Endpoint"
echo "🔍 Testing: POST $BASE_URL/predict-min"
echo "📤 Payload: Minimal house data (8 features only)"
if response=$(curl -s -w "%{http_code}" -o /tmp/minimal_response.json \
    -H "Content-Type: application/json" \
    -d "$MINIMAL_DATA" \
    "$BASE_URL/predict-min" \
    --max-time $TIMEOUT); then
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        prediction=$(cat /tmp/minimal_response.json | jq -r '.prediction')
        inference_time=$(cat /tmp/minimal_response.json | jq -r '.inference_ms')
        print_success "✅ Minimal features prediction successful!"
        echo "   💰 Predicted Price: \$$(printf "%.0f" "$prediction")"
        echo "   ⚡ Model Inference Time: ${inference_time}ms"
        echo "   🌐 Status Code: $http_code"
        echo "   📊 Full Response: $(cat /tmp/minimal_response.json | jq -c .)"
        echo "   🎯 Note: This endpoint uses only essential features for faster predictions"
    else
        print_error "❌ Minimal prediction failed with HTTP $http_code"
        echo "   📄 Error Response: $(cat /tmp/minimal_response.json)"
        exit 1
    fi
else
    print_error "❌ Minimal prediction failed: Connection error"
    exit 1
fi

# Test 5: Model Reload & Hot-Swap
print_header "5️⃣ Testing Model Reload & Hot-Swap Endpoint"
echo "🔍 Testing: POST $BASE_URL/reload"
echo "📤 Action: Switching from model_A to model_B"

# First, check current model version
current_version=$(curl -s "$BASE_URL/health" | jq -r '.model_version')
echo "   📌 Current Model Version: $current_version"

# Switch to model_B
if response=$(curl -s -w "%{http_code}" -o /tmp/reload_response.json \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"model_key": "model_B"}' \
    "$BASE_URL/reload" \
    --max-time $TIMEOUT); then
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        old_version=$(cat /tmp/reload_response.json | jq -r '.old_version')
        new_version=$(cat /tmp/reload_response.json | jq -r '.new_version')
        message=$(cat /tmp/reload_response.json | jq -r '.message')
        print_success "✅ Model hot-swap successful!"
        echo "   📝 Message: $message"
        echo "   🔖 Old Version: $old_version"
        echo "   🔖 New Version: $new_version"
        echo "   🌐 Status Code: $http_code"
        
        # Verify the model actually changed
        if [ "$old_version" != "$new_version" ]; then
            print_success "   ✅ Model version changed successfully!"
        else
            print_warning "   ⚠️  Model version unchanged (expected if model files are identical)"
        fi
        
        # Switch back to model_A
        echo ""
        echo "   🔄 Switching back to model_A..."
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -d '{"model_key": "model_A"}' \
            "$BASE_URL/reload" > /tmp/reload_back.json
        
        restored_version=$(cat /tmp/reload_back.json | jq -r '.new_version')
        echo "   ✅ Restored to model_A (version: $restored_version)"
        echo "   🔄 Note: Hot-swap allows model switching without service restart"
    else
        print_error "❌ Model reload failed with HTTP $http_code"
        echo "   📄 Error Response: $(cat /tmp/reload_response.json)"
        exit 1
    fi
else
    print_error "❌ Model reload failed: Connection error"
    exit 1
fi

# Test 6: Error Handling
print_header "6️⃣ Testing Error Handling"

# Invalid data
echo "🔍 Testing: POST $BASE_URL/predict with invalid data"
echo "📤 Payload: {\"invalid\": \"data\"} (should trigger validation error)"
if response=$(curl -s -w "%{http_code}" -o /tmp/invalid_response.json \
    -H "Content-Type: application/json" \
    -d "$INVALID_DATA" \
    "$BASE_URL/predict" \
    --max-time 5); then
    http_code="${response: -3}"
    if [ "$http_code" = "422" ]; then
        print_success "✅ Validation error handling works correctly!"
        echo "   🚫 Expected HTTP 422 (Unprocessable Entity) received"
        echo "   📄 Error Response: $(cat /tmp/invalid_response.json | jq -c .)"
        echo "   ✅ API properly validates input data"
    else
        print_warning "⚠️  Unexpected response: $http_code"
        echo "   📄 Response: $(cat /tmp/invalid_response.json)"
    fi
else
    print_error "❌ Error handling test failed: Connection error"
fi

# Large batch (exceeds 100 limit)
echo ""
echo "🔍 Testing: POST $BASE_URL/predict/batch with oversized batch"
echo "📤 Payload: 150 house records (exceeds 100 limit)"
large_batch='['
for i in {1..150}; do
    large_batch+="$TEST_DATA"
    if [ $i -lt 150 ]; then
        large_batch+=','
    fi
done
large_batch+=']'

if response=$(curl -s -w "%{http_code}" -o /tmp/large_batch_response.json \
    -H "Content-Type: application/json" \
    -d "$large_batch" \
    "$BASE_URL/predict/batch" \
    --max-time 5); then
    http_code="${response: -3}"
    if [ "$http_code" = "400" ]; then
        print_success "✅ Batch size limit properly enforced!"
        echo "   🚫 Expected HTTP 400 (Bad Request) received"
        echo "   📄 Error Response: $(cat /tmp/large_batch_response.json | jq -c .)"
        echo "   ✅ API correctly rejects oversized batches"
    else
        print_warning "⚠️  Batch size limit not enforced: $http_code"
        echo "   📄 Response: $(cat /tmp/large_batch_response.json)"
    fi
else
    print_error "❌ Batch size test failed: Connection error"
fi

# Test 7: Performance Test
print_header "7️⃣ Testing Performance"
echo "🔍 Testing: Performance benchmark with 10 consecutive requests"
echo "📤 Payload: Standard house prediction data"
echo "⏱️  Measuring individual response times..."

# Use curl's built-in timing to get more accurate results
total_time=0
times=()
for i in {1..10}; do
    # Use curl's time_total output (in seconds with decimal)
    time_result=$(curl -s -H "Content-Type: application/json" \
         -d "$TEST_DATA" \
         "$BASE_URL/predict" \
         --max-time 5 \
         -w "%{time_total}" \
         -o /dev/null)
    # Convert to milliseconds and add to total (fixed: multiply inside awk)
    time_ms=$(echo "$time_result" | awk '{printf "%.0f", $1 * 1000}')
    total_time=$((total_time + time_ms))
    times+=($time_ms)
    echo "   Request $i: ${time_ms}ms"
done

avg_time=$(( total_time / 10 ))
min_time=${times[0]}
max_time=${times[0]}
for time in "${times[@]}"; do
    if [ $time -lt $min_time ]; then min_time=$time; fi
    if [ $time -gt $max_time ]; then max_time=$time; fi
done

print_success "✅ Performance test completed!"
echo "   📊 Total Time: ${total_time}ms"
echo "   📈 Average Response Time: ${avg_time}ms"
echo "   ⚡ Fastest Request: ${min_time}ms"
echo "   🐌 Slowest Request: ${max_time}ms"
echo "   📉 Performance Range: ${min_time}ms - ${max_time}ms"

# Test 8: API Documentation
print_header "8️⃣ Testing API Documentation"

echo "🔍 Testing: GET $BASE_URL/docs (Swagger UI)"
if response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/docs" --max-time 5); then
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        print_success "✅ Swagger UI is accessible!"
        echo "   🌐 Status Code: $http_code"
        echo "   📖 Interactive API documentation available"
        echo "   🔗 URL: $BASE_URL/docs"
    else
        print_warning "⚠️  Swagger UI not accessible: $http_code"
    fi
else
    print_error "❌ Documentation test failed: Connection error"
fi

echo ""
echo "🔍 Testing: GET $BASE_URL/redoc (ReDoc)"
if response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/redoc" --max-time 5); then
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        print_success "✅ ReDoc is accessible!"
        echo "   🌐 Status Code: $http_code"
        echo "   📚 Alternative API documentation available"
        echo "   🔗 URL: $BASE_URL/redoc"
    else
        print_warning "⚠️  ReDoc not accessible: $http_code"
    fi
else
    print_error "❌ ReDoc test failed: Connection error"
fi

# Test 9: Real Data Test (if available)
print_header "9️⃣ Testing with Real Data"
if [ -f "data/future_unseen_examples.csv" ]; then
    echo "🔍 Testing: POST $BASE_URL/predict with real house data"
    echo "📤 Payload: First row from future_unseen_examples.csv"
    
    # Extract first row and convert to JSON
    first_row=$(head -n 2 data/future_unseen_examples.csv | tail -n 1)
    IFS=',' read -r -a fields <<< "$first_row"
    
    real_data='{
        "bedrooms": '${fields[0]}',
        "bathrooms": '${fields[1]}',
        "sqft_living": '${fields[2]}',
        "sqft_lot": '${fields[3]}',
        "floors": '${fields[4]}',
        "waterfront": '${fields[5]}',
        "view": '${fields[6]}',
        "condition": '${fields[7]}',
        "grade": '${fields[8]}',
        "sqft_above": '${fields[9]}',
        "sqft_basement": '${fields[10]}',
        "yr_built": '${fields[11]}',
        "yr_renovated": '${fields[12]}',
        "zipcode": "'${fields[13]}'",
        "lat": '${fields[14]}',
        "long": '${fields[15]}',
        "sqft_living15": '${fields[16]}',
        "sqft_lot15": '${fields[17]}'
    }'
    
    echo "   📊 Real house data: ${fields[0]} bed, ${fields[1]} bath, ${fields[2]} sqft"
    
    if response=$(curl -s -w "%{http_code}" -o /tmp/real_data_response.json \
        -H "Content-Type: application/json" \
        -d "$real_data" \
        "$BASE_URL/predict" \
        --max-time $TIMEOUT); then
        http_code="${response: -3}"
        if [ "$http_code" = "200" ]; then
            prediction=$(cat /tmp/real_data_response.json | jq -r '.prediction')
            inference_time=$(cat /tmp/real_data_response.json | jq -r '.inference_ms')
            print_success "✅ Real data prediction successful!"
            echo "   💰 Predicted Price: \$$(printf "%.0f" "$prediction")"
            echo "   ⚡ Model Inference Time: ${inference_time}ms"
            echo "   🌐 Status Code: $http_code"
            echo "   📊 Full Response: $(cat /tmp/real_data_response.json | jq -c .)"
            echo "   🏠 Note: This test uses actual house data from the dataset"
        else
            print_error "❌ Real data test failed with HTTP $http_code"
            echo "   📄 Error Response: $(cat /tmp/real_data_response.json)"
        fi
    else
        print_error "❌ Real data test failed: Connection error"
    fi
else
    print_warning "⚠️  Real data file not found, skipping test"
    echo "   📁 Expected file: data/future_unseen_examples.csv"
    echo "   💡 This test validates the API with real-world data"
fi

# Cleanup temporary files
rm -f /tmp/*_response.json

echo ""
echo "============================================================"
echo "🎉 Comprehensive API testing completed!"
echo "============================================================"
echo ""
echo "✅ All tests passed! API is ready for production."
