"""TC014: Test GET /notes without authentication."""

import pytest
import allure
import requests
import json
from config.environment import env_config


@allure.feature("API")
@allure.story("Notes API")
@allure.title("TC014: Test GET /notes without authentication")
@allure.description("Validate that GET /notes API returns 401 status code when accessed without authentication")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_notes_without_authentication():
    """Test that GET /notes API returns 401 when accessed without authentication."""
    
    # Get API configuration
    api_config = env_config.api_config
    api_url = env_config.api_url
    timeout = api_config.get("timeout", 30)
    
    # Construct API endpoint
    notes_endpoint = f"{api_url}/notes"
    
    # Send GET request to /notes endpoint WITHOUT authentication
    with allure.step("Send GET request to /notes endpoint without authentication"):
        allure.attach(
            f"API Endpoint: {notes_endpoint}\nTimeout: {timeout} seconds\nAuthentication: None (No token)",
            name="API Request Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        try:
            # Send GET request without authentication headers
            response = requests.get(
                notes_endpoint,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                    # Note: No x-auth-token header included
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
    
    # 🔹 Validate that status code is 401 (Unauthorized)
    with allure.step("Validate unauthorized access status code"):
        if response.status_code == 401:
            allure.attach(
                "Status code is 401 - ASSERT TRUE",
                name="Authentication Check Result",
                attachment_type=allure.attachment_type.TEXT
            )
            assert True, "GET /notes API correctly returns 401 without authentication"
        else:
            allure.attach(
                f"Status code is {response.status_code} (expected 401) - ASSERT FALSE",
                name="Authentication Check Result",
                attachment_type=allure.attachment_type.TEXT
            )
            assert False, f"Expected status code 401 without authentication, but got {response.status_code}"
    
    # Additional validation for 401 response
    with allure.step("Additional 401 response validation"):
        if response.status_code == 401:
            # Validate specific 401 response format
            try:
                response_data = response.json()
                
                # Check expected response structure
                expected_success = False
                expected_status = 401
                expected_message = "No authentication token specified in x-auth-token header"
                
                actual_success = response_data.get("success")
                actual_status = response_data.get("status")
                actual_message = response_data.get("message")
                
                # Validate success field
                if actual_success == expected_success:
                    allure.attach(
                        "success field is correct: false",
                        name="Success Field Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    success_valid = True
                else:
                    allure.attach(
                        f"success field is incorrect: expected {expected_success}, got {actual_success}",
                        name="Success Field Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    success_valid = False
                
                # Validate status field
                if actual_status == expected_status:
                    allure.attach(
                        "status field is correct: 401",
                        name="Status Field Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    status_valid = True
                else:
                    allure.attach(
                        f"status field is incorrect: expected {expected_status}, got {actual_status}",
                        name="Status Field Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    status_valid = False
                
                # Validate message field
                if actual_message == expected_message:
                    allure.attach(
                        "message field is correct: 'No authentication token specified in x-auth-token header'",
                        name="Message Field Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    message_valid = True
                else:
                    allure.attach(
                        f"message field is incorrect: expected '{expected_message}', got '{actual_message}'",
                        name="Message Field Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    message_valid = False
                
                # Overall response format validation
                if success_valid and status_valid and message_valid:
                    allure.attach(
                        "Response format matches expected 401 error structure",
                        name="Response Format Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                else:
                    allure.attach(
                        "Response format does not match expected 401 error structure",
                        name="Response Format Validation",
                        attachment_type=allure.attachment_type.TEXT
                    )
                        
            except json.JSONDecodeError:
                allure.attach(
                    "Response is not valid JSON - cannot validate error structure",
                    name="JSON Parsing Error",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # Validate content type for error response
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                allure.attach(
                    "Response has appropriate JSON content type for error",
                    name="Content Type Validation",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    f"Response content type: {content_type}",
                    name="Content Type Validation",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    # Test completion summary
    with allure.step("API test completion"):
        allure.attach(
            f"GET /notes API without authentication test completed\n"
            f"Endpoint: {notes_endpoint}\n"
            f"Status Code: {response.status_code}\n"
            f"Expected: 401\n"
            f"Response Time: {response.elapsed.total_seconds():.2f}s\n"
            f"Response Size: {len(response.content)} bytes\n"
            f"Authentication Test: {'PASSED' if response.status_code == 401 else 'FAILED'}",
            name="Test Summary",
            attachment_type=allure.attachment_type.TEXT
        )