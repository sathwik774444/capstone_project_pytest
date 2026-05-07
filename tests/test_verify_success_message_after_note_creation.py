"""TC007: Test verify success message after note creation."""

import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.notes_page import NotesPage
from config.environment import env_config


@allure.feature("Notes")
@allure.story("Note Creation")
@allure.title("TC007: Test verify success message after note creation")
@allure.description("Verify success message is displayed after creating a note")
@allure.severity(allure.severity_level.NORMAL)
def test_verify_success_message_after_note_creation(browser):
    """Test verifying success message after note creation."""
    # 🔹 Initialize pages
    login_page = LoginPage(browser)
    home_page = HomePage(browser)
    notes_page = NotesPage(browser)
    
    # 🔹 Navigate to login page and login
    login_page.navigate_to_login()
    valid_user = env_config.test_data["valid_user"]
    
    with allure.step("Login with valid credentials"):
        login_page.login(valid_user["username"], valid_user["password"])
    
    # 🔹 Verify login success
    with allure.step("Verify login success"):
        assert home_page.is_home_page_loaded(), "Login failed or home page not loaded"
    
    # 🔹 Wait for notes page to load
    with allure.step("Wait for notes page to load"):
        notes_page.wait_for_notes_page_load()
    
    # 🔹 Get test data
    note_data = env_config.test_data["note_data"]
    
    # 🔹 Create a new note (reuse the same logic from test_create_note_with_valid_details)
    with allure.step(f"Create note with title: {note_data['title']}"):
        notes_page.create_note(note_data['title'], note_data['description'])
    
    # 🔹 Verify success message after note creation
    with allure.step("Verify success message after note creation"):
        import time
        
        # Wait for success message to appear (give it some time)
        time.sleep(5)
        
        # Check if success message is displayed
        success_message_found = notes_page.is_success_message_displayed()
        
        if success_message_found:
            # Get the success message text
            success_message = notes_page.get_success_message()
            allure.attach(
                f"Success Message Found: {success_message}",
                name="Success Message",
                attachment_type=allure.attachment_type.TEXT
            )
            assert True, f"Success message displayed: {success_message}"
        else:
            # No success message found - this is the expected behavior
            allure.attach(
                "No success message found after note creation",
                name="Success Message Status",
                attachment_type=allure.attachment_type.TEXT
            )
            assert False , "No such message found - Note creation completed without success message"
                