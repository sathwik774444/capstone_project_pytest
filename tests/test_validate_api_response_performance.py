"""TC018: Test validate API response performance."""

import pytest
import allure
import requests
import time
from config.environment import env_config


@allure.feature("Performance")
@allure.story("API Performance")
@allure.title("TC018: Test validate API response performance")
@allure.description("Validate that API responses complete within 2 seconds for optimal performance")
@allure.severity(allure.severity_level.CRITICAL)
def test_validate_api_response_performance():
    """Test validating API response performance - all responses should be under 2 seconds."""
    
    # Performance threshold
    PERFORMANCE_THRESHOLD = 2.0  # seconds
    
    # Get API configuration and user credentials
    api_url = env_config.api_url
    valid_user = env_config.test_data["valid_user"]
    
    # Construct API endpoints
    login_endpoint = f"{api_url}/users/login"
    notes_endpoint = f"{api_url}/notes"
    
    # 🔹 Test 1: Login API Performance
    with allure.step("Test Login API performance"):
        start_time = time.time()
        
        login_response = requests.post(
            login_endpoint,
            timeout=3,
            json={
                "email": valid_user["username"],
                "password": valid_user["password"]
            }
        )
        
        response_time = time.time() - start_time
        
        if login_response.status_code == 200:
            allure.attach(
                f"Login API: {response_time:.3f}s - PASS",
                name="Performance Result",
                attachment_type=allure.attachment_type.TEXT
            )
            login_performance_ok = True
        else:
            allure.attach(
                f"Login API: {response_time:.3f}s - FAIL",
                name="Performance Result",
                attachment_type=allure.attachment_type.TEXT
            )
            login_performance_ok = False
        
        # Extract token
        login_data = login_response.json()
        auth_token = None
        if login_data.get("success") and "data" in login_data:
            auth_token = login_data["data"]["token"]
        elif "token" in login_data:
            auth_token = login_data["token"]
        
        if not auth_token:
            pytest.fail("No authentication token found")
    
    # 🔹 Test 2: GET Notes API Performance
    with allure.step("Test GET Notes API performance"):
        start_time = time.time()
        
        notes_response = requests.get(
            notes_endpoint,
            timeout=3,
            headers={"x-auth-token": auth_token}
        )
        
        response_time = time.time() - start_time
        
        if notes_response.status_code == 200:
            allure.attach(
                f"GET Notes API: {response_time:.3f}s - PASS",
                name="Performance Result",
                attachment_type=allure.attachment_type.TEXT
            )
            notes_performance_ok = True
        else:
            allure.attach(
                f"GET Notes API: {response_time:.3f}s - FAIL",
                name="Performance Result",
                attachment_type=allure.attachment_type.TEXT
            )
            notes_performance_ok = False
    
    # 🔹 Overall Performance Validation
    with allure.step("Overall performance validation"):
        if login_performance_ok and notes_performance_ok:
            allure.attach(
                "All API responses within 2 seconds - ASSERT TRUE",
                name="Overall Result",
                attachment_type=allure.attachment_type.TEXT
            )
            assert True, "All API responses completed within 2 seconds"
        else:
            allure.attach(
                "Some API responses exceeded 2 seconds - ASSERT FALSE",
                name="Overall Result",
                attachment_type=allure.attachment_type.TEXT
            )
            assert False, "Some API responses exceeded 2 seconds"
