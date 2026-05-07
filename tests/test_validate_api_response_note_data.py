"""TC013: Test validate API response note data."""

import pytest
import allure
import requests
import json
from config.environment import env_config


@allure.feature("API")
@allure.story("Notes API")
@allure.title("TC013: Test validate API response note data")
@allure.description("Validate that GET /notes API response contains complete note data with all required fields")
@allure.severity(allure.severity_level.CRITICAL)
def test_validate_api_response_note_data():
    """Test validating that GET /notes API response contains complete note data."""
    
    # Get API configuration and user credentials
    api_config = env_config.api_config
    api_url = env_config.api_url
    timeout = api_config.get("timeout", 30)
    valid_user = env_config.test_data["valid_user"]
    
    # Construct API endpoints
    login_endpoint = f"{api_url}/users/login"
    notes_endpoint = f"{api_url}/notes"
    
    # Required fields for each note
    required_fields = ["id", "title", "description", "category", "completed", "created_at", "updated_at", "user_id"]
    
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
    
    # 🔹 Validate status code 200 and extract notes list
    with allure.step("Validate status code 200 and extract notes list"):
        # Assert that status code is 200
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        
        # Extract notes list from response
        try:
            response_data = response.json()
            notes_list = None
            
            # Extract notes list from different possible response structures
            if isinstance(response_data, list):
                notes_list = response_data
            elif isinstance(response_data, dict):
                if "data" in response_data and isinstance(response_data["data"], list):
                    notes_list = response_data["data"]
                elif "notes" in response_data and isinstance(response_data["notes"], list):
                    notes_list = response_data["notes"]
                elif "items" in response_data and isinstance(response_data["items"], list):
                    notes_list = response_data["items"]
            
            assert notes_list is not None, "No notes list found in API response"
            allure.attach(
                f"✅ Notes list extracted with {len(notes_list)} notes",
                name="Notes List Extraction",
                attachment_type=allure.attachment_type.TEXT
            )
                
        except json.JSONDecodeError:
            assert False, "Response is not valid JSON"
    
    # 🔹 Validate note data completeness
    with allure.step("Validate note data completeness"):
        allure.attach(
            f"Required fields: {', '.join(required_fields)}",
            name="Required Fields",
            attachment_type=allure.attachment_type.TEXT
        )
        
        if len(notes_list) == 0:
            allure.attach(
                "⚠️ Notes list is empty - no note data to validate",
                name="Validation Warning",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.skip("No notes available for validation")
        
        # Validate each note in the list
        all_notes_valid = True
        validation_results = []
        
        for i, note in enumerate(notes_list):
            note_validation = {
                "note_index": i,
                "note_id": note.get("id", "N/A"),
                "missing_fields": [],
                "invalid_fields": [],
                "is_valid": True
            }
            
            # Check if note is a dictionary
            if not isinstance(note, dict):
                note_validation["is_valid"] = False
                note_validation["invalid_fields"].append(f"Note is not a dictionary (type: {type(note)})")
                all_notes_valid = False
                validation_results.append(note_validation)
                continue
            
            # Check for required fields
            present_fields = list(note.keys())
            missing_fields = [field for field in required_fields if field not in note]
            
            if missing_fields:
                note_validation["missing_fields"] = missing_fields
                note_validation["is_valid"] = False
                all_notes_valid = False
            
            # Validate field types and values
            field_validations = {}
            
            # Validate ID (should be string or number)
            if "id" in note:
                if not isinstance(note["id"], (str, int)):
                    note_validation["invalid_fields"].append(f"id field has invalid type: {type(note['id'])}")
                    note_validation["is_valid"] = False
            
            # Validate title (should be non-empty string)
            if "title" in note:
                if not isinstance(note["title"], str) or not note["title"].strip():
                    note_validation["invalid_fields"].append("title field should be non-empty string")
                    note_validation["is_valid"] = False
            
            # Validate description (should be string)
            if "description" in note:
                if not isinstance(note["description"], str):
                    note_validation["invalid_fields"].append("description field should be string")
                    note_validation["is_valid"] = False
            
            # Validate category (should be string)
            if "category" in note:
                if not isinstance(note["category"], str):
                    note_validation["invalid_fields"].append("category field should be string")
                    note_validation["is_valid"] = False
            
            # Validate completed (should be boolean)
            if "completed" in note:
                if not isinstance(note["completed"], bool):
                    note_validation["invalid_fields"].append("completed field should be boolean")
                    note_validation["is_valid"] = False
            
            # Validate created_at (should be string - datetime format)
            if "created_at" in note:
                if not isinstance(note["created_at"], str):
                    note_validation["invalid_fields"].append("created_at field should be string (datetime)")
                    note_validation["is_valid"] = False
            
            # Validate updated_at (should be string - datetime format)
            if "updated_at" in note:
                if not isinstance(note["updated_at"], str):
                    note_validation["invalid_fields"].append("updated_at field should be string (datetime)")
                    note_validation["is_valid"] = False
            
            # Validate user_id (should be string or number)
            if "user_id" in note:
                if not isinstance(note["user_id"], (str, int)):
                    note_validation["invalid_fields"].append(f"user_id field has invalid type: {type(note['user_id'])}")
                    note_validation["is_valid"] = False
            
            if note_validation["invalid_fields"]:
                all_notes_valid = False
            
            validation_results.append(note_validation)
        
        # Log validation results
        for result in validation_results:
            status = "VALID" if result["is_valid"] else "INVALID"
            details = []
            
            if result["missing_fields"]:
                details.append(f"Missing: {', '.join(result['missing_fields'])}")
            if result["invalid_fields"]:
                details.append(f"Invalid: {', '.join(result['invalid_fields'])}")
            
            detail_text = " - " + "; ".join(details) if details else ""
            
            allure.attach(
                f"Note {result['note_index']} (ID: {result['note_id']}) - {status}{detail_text}",
                name="Note Validation Result",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # Assert that all notes are valid
        if all_notes_valid:
            allure.attach(
                "All notes contain complete and valid data",
                name="Overall Validation Result",
                attachment_type=allure.attachment_type.TEXT
            )
            assert True, "All notes contain complete and valid data"
        else:
            invalid_count = sum(1 for r in validation_results if not r["is_valid"])
            allure.attach(
                f" {invalid_count} out of {len(notes_list)} notes have incomplete or invalid data",
                name="Overall Validation Result",
                attachment_type=allure.attachment_type.TEXT
            )
            assert False, f"{invalid_count} out of {len(notes_list)} notes have incomplete or invalid data"
    
    # 🔹 Test completion summary
    with allure.step("API test completion"):
        allure.attach(
            f"GET /notes API test completed successfully\n"
            f"Endpoint: {notes_endpoint}\n"
            f"Status Code: {response.status_code}\n"
            f"Response Time: {response.elapsed.total_seconds():.2f}s\n"
            f"Response Size: {len(response.content)} bytes\n"
            f"Notes Validated: {len(notes_list)}\n"
            f"Required Fields: {len(required_fields)}\n"
            f"Data Validation: {'✅ PASSED' if all_notes_valid else '❌ FAILED'}",
            name="Test Summary",
            attachment_type=allure.attachment_type.TEXT
        )