"""TC017: Test delete note with invalid ID."""

import pytest
import allure
import requests
import json
from config.environment import env_config


@allure.feature("API")
@allure.story("Notes API")
@allure.title("TC017: Test delete note with invalid ID")
@allure.description("Validate that DELETE /notes/{id} API returns proper error when deleting note with invalid ID")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_note_with_invalid_id():
    """Test deleting a note with invalid ID and validate error response."""
    
    # Get API configuration and user credentials
    api_config = env_config.api_config
    api_url = env_config.api_url
    timeout = api_config.get("timeout", 30)
    valid_user = env_config.test_data["valid_user"]
    
    # Construct API endpoints
    login_endpoint = f"{api_url}/users/login"
    notes_endpoint = f"{api_url}/notes"
    
    # Get invalid ID from config file
    invalid_note_id = env_config.test_data.get("invalid_note_id", "invalid_id_12345")
    
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
    
    # 🔹 Delete note with invalid ID
    with allure.step("Delete note with invalid ID"):
        delete_endpoint = f"{notes_endpoint}/{invalid_note_id}"
        
        allure.attach(
            f"DELETE Endpoint: {delete_endpoint}\nInvalid Note ID: {invalid_note_id}",
            name="Delete Request Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        try:
            # Send DELETE request with invalid ID
            delete_response = requests.delete(
                delete_endpoint,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "x-auth-token": auth_token
                }
            )
            
            # Log response details
            allure.attach(
                f"Delete Status Code: {delete_response.status_code}\nResponse Time: {delete_response.elapsed.total_seconds():.2f} seconds\nHeaders: {dict(delete_response.headers)}",
                name="Delete Response Details",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Log response body if available
            if delete_response.text:
                try:
                    delete_json = delete_response.json()
                    allure.attach(
                        json.dumps(delete_json, indent=2),
                        name="Delete Response Body",
                        attachment_type=allure.attachment_type.JSON
                    )
                except json.JSONDecodeError:
                    allure.attach(
                        delete_response.text,
                        name="Delete Response Body (Raw)",
                        attachment_type=allure.attachment_type.TEXT
                    )
            
        except requests.exceptions.RequestException as e:
            allure.attach(
                f"Delete request error: {str(e)}",
                name="Delete Request Error",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.fail(f"DELETE note request failed: {str(e)}")
    
    # 🔹 Validate error response for invalid ID
    with allure.step("Validate error response for invalid ID"):
        # Expected error response
        expected_success = False
        expected_status = 400
        expected_message = "Note ID must be a valid ID"
        
        try:
            response_data = delete_response.json()
            
            # Get actual response values
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
                    "status field is correct: 400",
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
                    "message field is correct: 'Note ID must be a valid ID'",
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
            
            # Overall validation result
            if success_valid and status_valid and message_valid:
                allure.attach(
                    "✅ Error response matches expected format - ASSERT TRUE",
                    name="Overall Validation Result",
                    attachment_type=allure.attachment_type.TEXT
                )
                assert True, "Invalid ID error response is correct"
            else:
                allure.attach(
                    "❌ Error response does not match expected format - ASSERT FALSE",
                    name="Overall Validation Result",
                    attachment_type=allure.attachment_type.TEXT
                )
                assert False, "Invalid ID error response is incorrect"
                
        except json.JSONDecodeError:
            allure.attach(
                "❌ Response is not valid JSON - cannot validate error structure - ASSERT FALSE",
                name="JSON Parsing Error",
                attachment_type=allure.attachment_type.TEXT
            )
            assert False, "Response is not valid JSON"
    
    # 🔹 Test completion summary
    with allure.step("API test completion"):
        allure.attach(
            f"DELETE note with invalid ID test completed\n"
            f"Endpoint: {delete_endpoint}\n"
            f"Invalid ID: {invalid_note_id}\n"
            f"Status Code: {delete_response.status_code}\n"
            f"Expected Status: 400\n"
            f"Expected Message: 'Note ID must be a valid ID'\n"
            f"Validation Result: {'PASSED' if success_valid and status_valid and message_valid else 'FAILED'}",
            name="Test Summary",
            attachment_type=allure.attachment_type.TEXT
        )
