"""TC016: Test delete note using API."""

import pytest
import allure
import requests
import json
from config.environment import env_config


@allure.feature("API")
@allure.story("Notes API")
@allure.title("TC016: Test delete note using API")
@allure.description("Validate that DELETE /notes/{id} API can successfully delete the latest note")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_note_using_api():
    """Test deleting a note using API by getting notes first and deleting the latest one."""
    
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
    
    # 🔹 Step 1: Get all notes from API (reference from test_get_notes)
    with allure.step("Get all notes from API"):
        allure.attach(
            f"API Endpoint: {notes_endpoint}\nTimeout: {timeout} seconds\nAuthentication: Bearer Token",
            name="API Request Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        try:
            # Send authenticated GET request to the notes endpoint
            get_response = requests.get(
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
                f"Status Code: {get_response.status_code}\nResponse Time: {get_response.elapsed.total_seconds():.2f} seconds\nHeaders: {dict(get_response.headers)}",
                name="API Response Details",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Log response body if available
            if get_response.text:
                try:
                    response_json = get_response.json()
                    allure.attach(
                        json.dumps(response_json, indent=2),
                        name="API Response Body",
                        attachment_type=allure.attachment_type.JSON
                    )
                except json.JSONDecodeError:
                    allure.attach(
                        get_response.text,
                        name="API Response Body (Raw)",
                        attachment_type=allure.attachment_type.TEXT
                    )
            
        except requests.exceptions.RequestException as e:
            allure.attach(
                f"Get notes request error: {str(e)}",
                name="Request Error",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.fail(f"GET /notes API request failed: {str(e)}")
    
    # 🔹 Step 2: Validate response and extract notes list
    with allure.step("Validate response and extract notes list"):
        # Assert that status code is 200
        assert get_response.status_code == 200, f"Expected status code 200, but got {get_response.status_code}"
        
        # Extract notes list from response
        try:
            response_data = get_response.json()
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
            
            initial_count = len(notes_list)
            allure.attach(
                f"✅ Notes list extracted with {initial_count} notes",
                name="Notes List Extraction",
                attachment_type=allure.attachment_type.TEXT
            )
                
        except json.JSONDecodeError:
            assert False, "Response is not valid JSON"
    
    # 🔹 Step 3: Check if notes exist to delete
    with allure.step("Check if notes exist to delete"):
        if initial_count == 0:
            allure.attach(
                "⚠️ No notes available to delete",
                name="Deletion Check",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.skip("No notes available for deletion")
        
        allure.attach(
            f"Found {initial_count} notes available for deletion",
            name="Deletion Check",
            attachment_type=allure.attachment_type.TEXT
        )
    
    # 🔹 Step 4: Identify the latest note to delete
    with allure.step("Identify the latest note to delete"):
        latest_note = None
        latest_note_id = None
        
        # Find the latest note (assuming the first note is the latest, or we can sort by created_at)
        if notes_list:
            # Try to find note with latest created_at timestamp
            notes_with_time = []
            for note in notes_list:
                if isinstance(note, dict) and "created_at" in note:
                    notes_with_time.append(note)
            
            if notes_with_time:
                # Sort by created_at (assuming ISO format)
                notes_with_time.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                latest_note = notes_with_time[0]
            else:
                # Fallback: take the first note
                latest_note = notes_list[0]
            
            latest_note_id = latest_note.get("id")
            
            allure.attach(
                f"Latest note identified:\n"
                f"ID: {latest_note_id}\n"
                f"Title: {latest_note.get('title', 'N/A')}\n"
                f"Description: {latest_note.get('description', 'N/A')}\n"
                f"Created: {latest_note.get('created_at', 'N/A')}",
                name="Latest Note Details",
                attachment_type=allure.attachment_type.TEXT
            )
        
        assert latest_note_id is not None, "Could not identify latest note ID"
    
    # 🔹 Step 5: Delete the latest note using API
    with allure.step("Delete the latest note using API"):
        delete_endpoint = f"{notes_endpoint}/{latest_note_id}"
        
        allure.attach(
            f"DELETE Endpoint: {delete_endpoint}\nNote ID: {latest_note_id}",
            name="Delete Request Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        try:
            # Send DELETE request
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
    
    # 🔹 Step 6: Validate deletion response
    with allure.step("Validate deletion response"):
        # Check for successful deletion status codes (200, 204, or 202)
        if delete_response.status_code in [200, 204, 202]:
            allure.attach(
                "✅ Note deletion successful - ASSERT TRUE",
                name="Deletion Result",
                attachment_type=allure.attachment_type.TEXT
            )
            deletion_successful = True
        else:
            allure.attach(
                f"❌ Note deletion failed with status {delete_response.status_code} - ASSERT FALSE",
                name="Deletion Result",
                attachment_type=allure.attachment_type.TEXT
            )
            deletion_successful = False
        
        assert deletion_successful, f"Expected successful deletion status (200/204/202), but got {delete_response.status_code}"
    
    # 🔹 Step 7: Verify note is actually deleted by fetching notes again
    with allure.step("Verify note is deleted by fetching notes again"):
        try:
            # Wait a moment for deletion to propagate
            import time
            time.sleep(1)
            
            # Fetch notes again
            verify_response = requests.get(
                notes_endpoint,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "x-auth-token": auth_token
                }
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                updated_notes_list = None
                
                # Extract notes list from response
                if isinstance(verify_data, list):
                    updated_notes_list = verify_data
                elif isinstance(verify_data, dict):
                    if "data" in verify_data and isinstance(verify_data["data"], list):
                        updated_notes_list = verify_data["data"]
                    elif "notes" in verify_data and isinstance(verify_data["notes"], list):
                        updated_notes_list = verify_data["notes"]
                    elif "items" in verify_data and isinstance(verify_data["items"], list):
                        updated_notes_list = verify_data["items"]
                
                final_count = len(updated_notes_list) if updated_notes_list else 0
                
                # Verify that count decreased by 1
                if final_count == initial_count - 1:
                    allure.attach(
                        "✅ Notes count decreased by 1 - deletion verified",
                        name="Deletion Verification",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    count_verified = True
                else:
                    allure.attach(
                        f"❌ Expected {initial_count - 1} notes, got {final_count}",
                        name="Deletion Verification",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    count_verified = False
                
                # Verify that the deleted note is no longer in the list
                deleted_note_still_exists = False
                if updated_notes_list:
                    for note in updated_notes_list:
                        if isinstance(note, dict) and note.get("id") == latest_note_id:
                            deleted_note_still_exists = True
                            break
                
                if not deleted_note_still_exists:
                    allure.attach(
                        "✅ Deleted note no longer exists in notes list",
                        name="Deletion Verification",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    note_verified = True
                else:
                    allure.attach(
                        "❌ Deleted note still exists in notes list",
                        name="Deletion Verification",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    note_verified = False
                
                # Overall verification result
                if count_verified and note_verified:
                    allure.attach(
                        "✅ Note deletion fully verified",
                        name="Overall Verification Result",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    assert True, "Note deletion successful and verified"
                else:
                    allure.attach(
                        "❌ Note deletion verification failed",
                        name="Overall Verification Result",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    assert False, "Note deletion verification failed"
            else:
                allure.attach(
                    f"❌ Failed to verify deletion: {verify_response.status_code}",
                    name="Verification Error",
                    attachment_type=allure.attachment_type.TEXT
                )
                assert False, f"Failed to verify deletion: {verify_response.status_code}"
                
        except requests.exceptions.RequestException as e:
            allure.attach(
                f"Verification request error: {str(e)}",
                name="Verification Error",
                attachment_type=allure.attachment_type.TEXT
            )
            assert False, f"Error verifying deletion: {str(e)}"
    
    # 🔹 Test completion summary
    with allure.step("API test completion"):
        allure.attach(
            f"DELETE note API test completed\n"
            f"Endpoint: {delete_endpoint}\n"
            f"Initial Notes Count: {initial_count}\n"
            f"Final Notes Count: {final_count}\n"
            f"Deleted Note ID: {latest_note_id}\n"
            f"Delete Status Code: {delete_response.status_code}\n"
            f"Deletion Result: {'SUCCESSFUL' if deletion_successful else 'FAILED'}",
            name="Test Summary",
            attachment_type=allure.attachment_type.TEXT
        )
