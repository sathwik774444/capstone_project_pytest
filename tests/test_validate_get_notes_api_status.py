"""TC011: Test validate GET /notes API status."""

import pytest
import allure
import requests
import json
from config.environment import env_config


@allure.feature("API")
@allure.story("Notes API")
@allure.title("TC011: Test validate GET /notes API status")
@allure.description("Validate that GET /notes API endpoint returns status 200 with authentication")
@allure.severity(allure.severity_level.CRITICAL)
def test_validate_get_notes_api_status():
    """Test validating GET /notes API endpoint status with authentication."""
    
    # Get API configuration and user credentials
    api_config = env_config.api_config
    api_url = env_config.api_url
    timeout = api_config.get("timeout", 30)
    valid_user = env_config.test_data["valid_user"]
    
    # Construct API endpoints
    login_endpoint = f"{api_url}/users/login"
    notes_endpoint = f"{api_url}/notes"
    
    # Authenticate using login API to get token
    with allure.step("Authenticate using login API"):
        allure.attach(
            f"Login Endpoint: {login_endpoint}\nEmail: {valid_user['username']}",
            name="Authentication Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        try:
            # Send login request
            login_response = requests.post(
                login_endpoint,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "email": valid_user["username"],
                    "password": valid_user["password"]
                }
            )
            
            allure.attach(
                f"Login Status Code: {login_response.status_code}\nResponse Time: {login_response.elapsed.total_seconds():.2f}s",
                name="Login Response Details",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Handle login response
            if login_response.status_code == 200:
                try:
                    login_data = login_response.json()
                    allure.attach(
                        json.dumps(login_data, indent=2),
                        name="Login Response Body",
                        attachment_type=allure.attachment_type.JSON
                    )
                    
                    # Extract token from response based on exact API schema
                    auth_token = None
                    
                    # Check if response follows the expected schema: {"success": true, "data": {"token": "..."}}
                    if login_data.get("success") and "data" in login_data:
                        data = login_data["data"]
                        if "token" in data:
                            auth_token = data["token"]
                    
                    # Fallback: Check direct token field
                    if not auth_token and "token" in login_data:
                        auth_token = login_data["token"]
                    
                    if auth_token:
                        allure.attach(
                            f"✅ Authentication successful - Token obtained (length: {len(auth_token)})",
                            name="Authentication Status",
                            attachment_type=allure.attachment_type.TEXT
                        )
                    else:
                        allure.attach(
                            "❌ No token found in login response",
                            name="Authentication Status",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        pytest.fail("No authentication token found in login response")
                        
                except json.JSONDecodeError:
                    allure.attach(
                        login_response.text,
                        name="Login Response Body (Raw)",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    pytest.fail("Login response is not valid JSON")
                    
            else:
                allure.attach(
                    f"❌ Login failed with status {login_response.status_code}",
                    name="Authentication Status",
                    attachment_type=allure.attachment_type.TEXT
                )
                if login_response.text:
                    allure.attach(
                        login_response.text,
                        name="Login Error Response",
                        attachment_type=allure.attachment_type.TEXT
                    )
                pytest.fail(f"Login API request failed with status {login_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            allure.attach(
                f"Login request error: {str(e)}",
                name="Login Error",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.fail(f"Login API request failed: {str(e)}")
    
    # Send GET request to /notes endpoint with authentication
    with allure.step("Send authenticated GET request to /notes endpoint"):
        allure.attach(
            f"API Endpoint: {notes_endpoint}\nTimeout: {timeout} seconds\nAuthentication: Bearer Token",
            name="API Request Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        try:
            # Send authenticated GET request to the notes endpoint
            response = requests.get(
                notes_endpoint,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "x-auth-token": auth_token
                }
            )
            
            # Log response details
            allure.attach(
                f"Status Code: {response.status_code}\nResponse Time: {response.elapsed.total_seconds():.2f} seconds\nHeaders: {dict(response.headers)}",
                name="API Response Details",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Log response body if available
            if response.text:
                try:
                    response_json = response.json()
                    allure.attach(
                        json.dumps(response_json, indent=2),
                        name="API Response Body",
                        attachment_type=allure.attachment_type.JSON
                    )
                except json.JSONDecodeError:
                    allure.attach(
                        response.text,
                        name="API Response Body (Raw)",
                        attachment_type=allure.attachment_type.TEXT
                    )
            
        except requests.exceptions.Timeout:
            allure.attach(
                f"Request timed out after {timeout} seconds",
                name="Request Timeout",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.fail(f"GET /notes API request timed out after {timeout} seconds")
            
        except requests.exceptions.ConnectionError as e:
            allure.attach(
                f"Connection error: {str(e)}",
                name="Connection Error",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.fail(f"Failed to connect to GET /notes API: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            allure.attach(
                f"Request error: {str(e)}",
                name="Request Error",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.fail(f"GET /notes API request failed: {str(e)}")
    
    # 🔹 Validate response status
    with allure.step("Validate API response status"):
        # Assert that status code is 200 (with authentication)
        assert response.status_code == 200, f"Expected status code 200 with authentication, but got {response.status_code}"
        
        allure.attach(
            "✅ Status code validation passed: 200 OK",
            name="Status Validation Result",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Additional validations for successful response
        with allure.step("Additional response validations"):
            # Check that response has content
            assert len(response.content) > 0, "Response body is empty"
            
            # Check that response has proper content type if headers are present
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                # If JSON response, validate it's valid JSON
                try:
                    response.json()
                    allure.attach(
                        "✅ Response is valid JSON",
                        name="JSON Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                except json.JSONDecodeError:
                    allure.attach(
                        "⚠️ Response claims to be JSON but is not valid",
                        name="JSON Validation Warning",
                        attachment_type=allure.attachment_type.TEXT
                    )
            
            # Log response time performance
            response_time = response.elapsed.total_seconds()
            allure.attach(
                f"Response time: {response_time:.2f} seconds",
                name="Performance Metrics",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Assert reasonable response time (less than 10 seconds)
            assert response_time < 10.0, f"Response time {response_time:.2f}s is too slow (should be < 10s)"
    
    # 🔹 Test completion summary
    with allure.step("API test completion"):
        allure.attach(
            f"GET /notes API test completed successfully\n"
            f"Endpoint: {notes_endpoint}\n"
            f"Status Code: {response.status_code}\n"
            f"Response Time: {response.elapsed.total_seconds():.2f}s\n"
            f"Response Size: {len(response.content)} bytes",
            name="Test Summary",
            attachment_type=allure.attachment_type.TEXT
        )