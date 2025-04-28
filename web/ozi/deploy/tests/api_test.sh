#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HOST="localhost"
PORT="2169"  # Default flask app port, adjust as needed
ADMIN_KEY="change_this_to_a_secure_random_value"  # Default admin key, replace with your actual key
OUTPUT_DIR="api_test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Test tracking
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to run a test
run_test() {
    DESCRIPTION=$1
    ENDPOINT=$2
    METHOD=${3:-"GET"}
    EXPECTED_STATUS=${4:-200}
    OUTPUT_FILE="$OUTPUT_DIR/${TIMESTAMP}_$(echo $DESCRIPTION | tr ' ' '_').out"
    
    TOTAL_TESTS=$((TOTAL_TESTS+1))
    
    echo -e "${BLUE}Running test: ${DESCRIPTION}${NC}"
    echo "Endpoint: $ENDPOINT"
    echo "Method: $METHOD"
    echo "Expected status: $EXPECTED_STATUS"
    
    # Run the curl command
    HTTP_STATUS=$(curl -s -o "$OUTPUT_FILE" -w "%{http_code}" -X "$METHOD" "$ENDPOINT")
    
    # Check if status matches expected
    if [ "$HTTP_STATUS" -eq "$EXPECTED_STATUS" ]; then
        echo -e "${GREEN}PASSED${NC} - Got expected status $HTTP_STATUS"
        PASSED_TESTS=$((PASSED_TESTS+1))
    else
        echo -e "${RED}FAILED${NC} - Expected status $EXPECTED_STATUS, got $HTTP_STATUS"
    fi
    
    # Show preview of output
    echo -e "${YELLOW}Response preview:${NC}"
    head -n 10 "$OUTPUT_FILE"
    if [ $(wc -l < "$OUTPUT_FILE") -gt 10 ]; then
        echo -e "${YELLOW}... (truncated, see full output in $OUTPUT_FILE)${NC}"
    fi
    
    echo ""
}

echo -e "${BLUE}===== CTF Deployer API Test Script =====${NC}"
echo "Testing against: http://$HOST:$PORT"
echo "Results will be saved to: $OUTPUT_DIR"
echo ""

# Test 1: Basic health check
run_test "Health Check" "http://$HOST:$PORT/health"

# Test 2: Basic status endpoint (no auth)
run_test "Basic Status" "http://$HOST:$PORT/status"

# Test 3: Admin status with auth
run_test "Admin Status" "http://$HOST:$PORT/admin/status?admin_key=$ADMIN_KEY"

# Test 4: Admin status with invalid auth
run_test "Admin Status (Invalid Auth)" "http://$HOST:$PORT/admin/status?admin_key=invalid_key" "GET" 403

# Log endpoints tests

# Test 5: All user containers logs (text format)
run_test "All User Container Logs (Text)" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&format=text"

# Test 6: All user containers logs (JSON format)
run_test "All User Container Logs (JSON)" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&format=json"

# Test 7: Deployer service logs
run_test "Deployer Service Logs" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&container_id=deployer&format=text"

# Test 8: Database service logs
run_test "Database Service Logs" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&container_id=database&format=text"

# Test 9: Task service logs
run_test "Task Service Logs" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&container_id=task_service&format=text"

# Test 10: All services logs
run_test "All Services Logs" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&container_id=all_services&format=text"

# Test 11: All logs (services and user containers)
run_test "All Logs (Services + Containers)" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&container_id=all&format=text"

# Test 12: Test log limits with tail parameter
run_test "Limited Logs (10 lines)" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&container_id=deployer&format=text&tail=10"

# Test 13: Test invalid container_id
run_test "Invalid Container ID" "http://$HOST:$PORT/logs?admin_key=$ADMIN_KEY&container_id=invalid_container" "GET" 404

# Test 14: Test logs without admin key
run_test "Logs Without Auth" "http://$HOST:$PORT/logs?container_id=deployer" "GET" 403

# Test 15: Test Prometheus metrics endpoint
run_test "Prometheus Metrics" "http://$HOST:$PORT/metrics?admin_key=$ADMIN_KEY"

# Print summary
echo -e "${BLUE}===== Test Summary =====${NC}"
echo -e "Total tests: $TOTAL_TESTS"
echo -e "Passed tests: ${GREEN}$PASSED_TESTS${NC}"
FAILED_TESTS=$((TOTAL_TESTS-PASSED_TESTS))
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "Failed tests: ${GREEN}0${NC}"
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "Failed tests: ${RED}$FAILED_TESTS${NC}"
    echo -e "${RED}Some tests failed.${NC}"
fi

echo ""
echo "Test results saved to $OUTPUT_DIR directory"
