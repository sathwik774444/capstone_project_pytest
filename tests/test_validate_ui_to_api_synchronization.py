"""TC018: Test validate UI to API synchronization for note creation."""

import pytest
import allure
import requests
import json
import time
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.notes_page import NotesPage
from config.environment import env_config


@allure.feature("UI-API Integration")
@allure.story("Note Creation Synchronization")
@allure.title("TC018: Test validate UI to API synchronization for note creation")
@allure.description("Ensure that creating a note through the UI makes it available in the API notes list")
@allure.severity(allure.severity_level.CRITICAL)
def test_validate_ui_to_api_synchronization(browser):
    """Test that UI note creation synchronizes with API by making note available in API response."""

    # ==========================================
    # CONFIGURATION
    # ==========================================

    api_config = env_config.api_config
    api_url = env_config.api_url
    timeout = api_config.get("timeout", 30)

    valid_user = env_config.test_data["valid_user"]
    note_data = env_config.test_data["note_data"]

    login_endpoint = f"{api_url}/users/login"
    notes_endpoint = f"{api_url}/notes"

    created_note_title = None
    auth_token = None

    # ==========================================
    # STEP 1 - CREATE NOTE THROUGH UI
    # ==========================================

    with allure.step("Create note through UI"):
        
        # Initialize pages
        login_page = LoginPage(browser)
        home_page = HomePage(browser)
        notes_page = NotesPage(browser)
        
        # Navigate to login page and login
        login_page.navigate_to_login()
        
        with allure.step("Login with valid credentials"):
            login_page.login(valid_user["username"], valid_user["password"])
        
        # Verify login success
        with allure.step("Verify login success"):
            assert home_page.is_home_page_loaded(), "Login failed or home page not loaded"
        
        # Wait for notes page to load
        with allure.step("Wait for notes page to load"):
            notes_page.wait_for_notes_page_load()
        
        # Get initial notes count
        initial_notes_count = notes_page.get_notes_count()
        
        # Create a new note through UI
        with allure.step(f"Create note with title: {note_data['title']}"):
            notes_page.create_note(note_data['title'], note_data['description'])
            created_note_title = note_data['title']
        
        # Verify note creation success in UI
        with allure.step("Verify note creation success in UI"):
            time.sleep(2)  # Wait for note to be created
            assert notes_page.is_note_with_title_visible(note_data['title']), \
                f"Note with title '{note_data['title']}' should be visible in UI"
        
        # Log UI creation results
        final_notes_count = notes_page.get_notes_count()
        allure.attach(
            f"Note Created Successfully in UI!\n"
            f"Title: {note_data['title']}\n"
            f"Description: {note_data['description']}\n"
            f"Initial Notes Count: {initial_notes_count}\n"
            f"Final Notes Count: {final_notes_count}",
            name="UI Note Creation Details",
            attachment_type=allure.attachment_type.TEXT
        )

    # ==========================================
    # STEP 2 - LOGIN VIA API TO GET TOKEN
    # ==========================================

    with allure.step("Login via API to get authentication token"):
        
        try:
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

            print("API LOGIN STATUS:", login_response.status_code)
            print("API LOGIN RESPONSE:", login_response.text)

            allure.attach(
                login_response.text,
                name="API Login Response",
                attachment_type=allure.attachment_type.TEXT
            )

            assert login_response.status_code == 200, \
                f"API login failed: {login_response.status_code}"

            login_data = login_response.json()
            auth_token = login_data["data"]["token"]

            assert auth_token is not None, \
                "Authentication token not found in API response"

            allure.attach(
                f"✅ API Authentication successful - Token obtained",
                name="API Authentication Status",
                attachment_type=allure.attachment_type.TEXT
            )

        except requests.exceptions.RequestException as e:
            pytest.fail(f"API login request failed: {str(e)}")

    # ==========================================
    # STEP 3 - GET ALL NOTES FROM API
    # ==========================================

    with allure.step("Get all notes from API"):
        
        try:
            get_notes_response = requests.get(
                notes_endpoint,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "x-auth-token": auth_token
                }
            )

            print("GET NOTES STATUS:", get_notes_response.status_code)
            print("GET NOTES RESPONSE:", get_notes_response.text)

            allure.attach(
                get_notes_response.text,
                name="Get Notes API Response",
                attachment_type=allure.attachment_type.TEXT
            )

            assert get_notes_response.status_code == 200, \
                f"Failed to get notes from API: {get_notes_response.status_code}"

            api_notes_data = get_notes_response.json()

            allure.attach(
                json.dumps(api_notes_data, indent=2),
                name="API Notes Response Body",
                attachment_type=allure.attachment_type.JSON
            )

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Get notes API request failed: {str(e)}")

    # ==========================================
    # STEP 4 - VALIDATE CREATED NOTE IN API RESPONSE
    # ==========================================

    with allure.step("Validate created note is visible in API response"):
        
        # Extract notes list from API response
        notes_list = []
        
        if isinstance(api_notes_data, list):
            notes_list = api_notes_data
        elif isinstance(api_notes_data, dict):
            if "data" in api_notes_data and isinstance(api_notes_data["data"], list):
                notes_list = api_notes_data["data"]
            elif "notes" in api_notes_data and isinstance(api_notes_data["notes"], list):
                notes_list = api_notes_data["notes"]
            elif "items" in api_notes_data and isinstance(api_notes_data["items"], list):
                notes_list = api_notes_data["items"]
        
        # Extract all note titles from API response
        api_note_titles = []
        for note in notes_list:
            if isinstance(note, dict):
                if "title" in note:
                    api_note_titles.append(note["title"])
                elif "name" in note:
                    api_note_titles.append(note["name"])
        
        allure.attach(
            json.dumps(api_note_titles, indent=2),
            name="API Note Titles",
            attachment_type=allure.attachment_type.JSON
        )

        # Check if the UI-created note is present in API response
        created_note_found_in_api = any(
            created_note_title in note_title
            for note_title in api_note_titles
        )

        if created_note_found_in_api:
            allure.attach(
                f"✅ UI-created note '{created_note_title}' found in API response",
                name="Synchronization Validation",
                attachment_type=allure.attachment_type.TEXT
            )
        else:
            allure.attach(
                f"❌ UI-created note '{created_note_title}' NOT found in API response",
                name="Synchronization Validation",
                attachment_type=allure.attachment_type.TEXT
            )
            allure.attach(
                f"Expected: '{created_note_title}'\n"
                f"Found in API: {api_note_titles}",
                name="Note Comparison Details",
                attachment_type=allure.attachment_type.TEXT
            )

        assert created_note_found_in_api, \
            f"UI-created note '{created_note_title}' should be visible in API response"

    # ==========================================
    # STEP 5 - VALIDATE NOTE DETAILS MATCH
    # ==========================================

    with allure.step("Validate note details match between UI and API"):
        
        # Find the created note in API response
        created_note_in_api = None
        for note in notes_list:
            if isinstance(note, dict):
                note_title = note.get("title") or note.get("name")
                if note_title and created_note_title in note_title:
                    created_note_in_api = note
                    break
        
        if created_note_in_api:
            api_description = created_note_in_api.get("description", "")
            ui_description = note_data["description"]
            
            description_matches = api_description == ui_description
            
            allure.attach(
                f"UI Description: {ui_description}\n"
                f"API Description: {api_description}\n"
                f"Descriptions Match: {description_matches}",
                name="Note Details Comparison",
                attachment_type=allure.attachment_type.TEXT
            )
            
            if description_matches:
                allure.attach(
                    "✅ Note details match perfectly between UI and API",
                    name="Details Validation",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    "⚠️ Note descriptions differ between UI and API",
                    name="Details Validation",
                    attachment_type=allure.attachment_type.TEXT
                )

    # ==========================================
    # TEST SUMMARY
    # ==========================================

    with allure.step("UI-API synchronization test summary"):
        
        allure.attach(
            f"""
            UI-API Synchronization Test Completed
            
            Created Note Title: {created_note_title}
            UI Notes Count: {final_notes_count}
            API Notes Count: {len(notes_list)}
            API Status Code: {get_notes_response.status_code}
            Note Found in API: {created_note_found_in_api}
            
            Synchronization Status: {'✅ SUCCESS' if created_note_found_in_api else '❌ FAILED'}
            """,
            name="Test Execution Summary",
            attachment_type=allure.attachment_type.TEXT
        )