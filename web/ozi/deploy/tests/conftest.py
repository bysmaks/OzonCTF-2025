"""
Pytest configuration file for CTF Deployer tests
This file contains common fixtures and configuration for all tests
"""
import os
import sys
import pytest
from dotenv import load_dotenv

# Add the project root to the Python path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add flask_app directory for direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../flask_app')))

# Load environment variables
load_dotenv()

# Print some helpful information when starting tests
def pytest_configure(config):
    """Print useful information about the test environment"""
    print("\n=== CTF Deployer Test Suite ===")
    print(f"Python version: {sys.version}")
    print(f"Project path: {os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}")
    print(f"Database: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
    print("---------------------------------")

@pytest.fixture(autouse=True)
def test_case_info(request):
    """Print test case name before and after each test for better readability"""
    print(f"\n----- Running test: {request.node.name} -----")
    yield
    print(f"----- Completed test: {request.node.name} -----")
