#!/bin/bash
# Serpent's Hidden Path CTF Challenge - Debug and Testing Script
# This script tests all aspects of the CTF challenge

# Set text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Set the target server - change this to your actual server IP/hostname
TARGET=${1:-"snak.ctf.local"}
PORT=${2:-"44444"}
BASE_URL="http://$TARGET:$PORT"

echo -e "${BOLD}${BLUE}=== Serpent's Hidden Path CTF Challenge Testing Script ===${NC}\n"
echo -e "Testing server: ${BOLD}$BASE_URL${NC}\n"

# Function to display section headers
section() {
    echo -e "\n${BOLD}${YELLOW}=== $1 ===${NC}\n"
}

# Function to make requests and display results
request() {
    local method=$1
    local url=$2
    local host=$3
    local description=$4
    
    echo -e "${BOLD}${description}${NC}"
    echo -e "${BLUE}Command:${NC} curl -s -i -X $method $url ${host:+-H \"Host: $host\"}"
    
    # Add -I for HEAD requests to see headers
    local curl_opts="-s -i"
    if [ "$method" == "HEAD" ]; then
        curl_opts="-s -i -I"
    fi
    
    # Make the request
    local response
    if [ -n "$host" ]; then
        response=$(curl $curl_opts -X "$method" "$url" -H "Host: $host")
    else
        response=$(curl $curl_opts -X "$method" "$url")
    fi
    
    # Extract status line
    local status_line=$(echo "$response" | head -n 1)
    echo -e "${BLUE}Status:${NC} $status_line"
    
    # Check for key headers
    if echo "$response" | grep -q "X-Debug-Info"; then
        local debug_info=$(echo "$response" | grep "X-Debug-Info" | head -1)
        echo -e "${GREEN}$debug_info${NC}"
    fi
    
    if echo "$response" | grep -q "X-Hint"; then
        local hint=$(echo "$response" | grep "X-Hint" | head -1)
        echo -e "${GREEN}$hint${NC}"
    fi
    
    if echo "$response" | grep -q "X-Red-Herring"; then
        local red_herring=$(echo "$response" | grep "X-Red-Herring" | head -1)
        echo -e "${RED}$red_herring${NC}"
    fi
    
    # Check for flag parts
    if echo "$response" | grep -q "X-Flag-Part"; then
        local flag_part=$(echo "$response" | grep "X-Flag-Part")
        echo -e "${BOLD}${GREEN}FLAG PART FOUND:${NC} $flag_part"
    fi
    
    # Check for Location header
    if echo "$response" | grep -q "Location"; then
        local location=$(echo "$response" | grep "Location" | head -1)
        echo -e "${BLUE}$location${NC}"
    fi
    
    echo -e "${BLUE}-----------------------------------------------------${NC}"
}

# Test 1: Access visible snake game with normal domain
section "Testing Visible Snake Game (Normal Domain)"
request "GET" "$BASE_URL/snake" "snake.ctf.local" "Accessing the normal snake game with correct host"

# Test 2: Access the hint endpoint
section "Testing Hint Endpoint"
request "GET" "$BASE_URL/hint" "snake.ctf.local" "Checking for hints"

# Test 3: Test default server behavior with different host headers
section "Testing Secret Server (NGINX Default Server Behavior)"
request "GET" "$BASE_URL/snake" "" "Accessing with empty Host header"
request "GET" "$BASE_URL/snake" "nonexistent.domain" "Accessing with non-matching hostname"
request "GET" "$BASE_URL/" "" "Accessing root with empty Host header"

# Test 4: Test HTTP methods on flag-piece endpoint
section "Testing HTTP Methods on /flag-piece (First Flag Part)"
request "OPTIONS" "$BASE_URL/flag-piece" "" "Using OPTIONS method to find flag part 1"

section "Testing HTTP Methods on /flag-piece (Third Flag Part)"
request "HEAD" "$BASE_URL/flag-piece" "" "Using HEAD method to find flag part 3"

# Test 5: Test port redirection
section "Testing Port Redirection (Custom Port Behavior)"
# For demonstration - we can't actually change ports in this script
echo -e "${BOLD}To test port redirection, try these commands manually:${NC}"
echo -e "curl -v -H \"Host: 127.0.0.1:9000\" $BASE_URL/snake"
echo -e "curl -v http://127.0.0.1:9000/snake  # If you can bind to this port"
echo -e "${BLUE}Should redirect to: http://snake.ctf.local:9000/snake${NC}"

# Test 6: Assemble the flag
section "Flag Assembly"
echo -e "${BOLD}The three parts of the flag are:${NC}"
echo -e "1. ${GREEN}CTF{nginx_${NC} (via OPTIONS to /flag-piece)"
echo -e "2. ${GREEN}default_server_first_${NC} (via collecting special food in the secret snake game)"
echo -e "3. ${GREEN}alphabetical}${NC} (via HEAD to /flag-piece)"
echo -e "\n${BOLD}${GREEN}Complete flag: CTF{nginx_default_server_first_alphabetical}${NC}"

section "Testing Summary"
echo -e "1. There are two snake games:"
echo -e "   - ${BLUE}Visible game:${NC} Accessed with proper host names (snake.ctf.local)"
echo -e "   - ${BLUE}Secret game:${NC} Accessed with non-matching or empty host headers"
echo -e "2. The secret game has special golden food items worth 50 points"
echo -e "3. The challenge leverages NGINX's alphabetical file loading order"
echo -e "4. ${BOLD}Key insight:${NC} With multiple server blocks, NGINX uses the first one defined"
echo -e "   for requests with non-matching host names"
echo -e "5. 20-prize.conf loads before 90-decoy.conf and becomes the effective default"

echo -e "\n${BOLD}${BLUE}=== Debug Script Completed ===${NC}\n"
